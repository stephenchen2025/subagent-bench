"""Run the adapter against the REAL Harbor base class.

Harbor needs Python >= 3.12 and is not on PyPI, so these tests skip unless it is
importable. When it is, they check the parts of the contract that only the real
class can settle: that our agent satisfies the abstract interface, that mini's
synchronous loop can actually be driven from inside Harbor's async `run()`, and
that the artifacts and usage land where Harbor expects.

Verified against harbor 0.22.0 and mini-swe-agent 2.4.6. No API key, no network.
"""

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytest.importorskip("harbor", reason="harbor requires Python >= 3.12")
mini = pytest.importorskip("minisweagent.agents.default")

from harbor.environments.base import ExecResult  # noqa: E402
from harbor.models.agent.context import AgentContext  # noqa: E402

from harness.harbor_agent import (  # noqa: E402
    HarborEnvBridge,
    build_agent_class,
    load_spec,
    populate_context,
)
from harness.templates import REPORT_CLOSE, REPORT_OPEN  # noqa: E402
from tests.test_mini_integration import DONE, ScriptedModel  # noqa: E402

F10 = json.loads((ROOT / "tasks/examples/f10_handback_wrong_pushback.json").read_text())


class FakeHarborEnv:
    """Minimal stand-in for BaseEnvironment: async exec returning ExecResult."""

    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.calls = []

    async def exec(self, command, cwd=None, env=None, timeout_sec=None, user=None):
        self.calls.append((command, cwd))
        await asyncio.sleep(0)  # a real environment yields; make sure we can too
        out = self._outputs.pop(0) if self._outputs else ""
        return ExecResult(stdout=out, stderr="", return_code=0)


def _report(text):
    return f"{REPORT_OPEN}{text}{REPORT_CLOSE}"


# --- contract -------------------------------------------------------------

def test_agent_class_satisfies_harbors_abstract_interface():
    cls = build_agent_class()
    assert cls.__abstractmethods__ == frozenset()
    assert cls.name() == "handoff-mini"


def test_agent_declares_the_resume_capability():
    """Harbor can drive a second turn natively; F10 does not depend on it."""
    assert build_agent_class().capabilities.resume is True


def test_agent_constructs_with_harbors_signature(tmp_path):
    cls = build_agent_class()
    agent = cls(tmp_path, model_name="test/model")
    assert agent.logs_dir == tmp_path
    assert agent.version()


def test_spec_path_option_is_accepted(tmp_path):
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(F10))
    agent = build_agent_class()(tmp_path, model_name="m", spec_path=str(spec_file))
    assert agent.options.spec_path == str(spec_file)
    assert load_spec(spec_file)["id"] == F10["id"]


def test_unknown_option_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="Unknown option"):
        build_agent_class()(tmp_path, model_name="m", nonsense=True)


# --- the async/sync bridge ------------------------------------------------

def test_bridge_drives_async_exec_from_a_worker_thread():
    """The crux: mini blocks on execute(); Harbor's exec is a coroutine."""

    async def scenario():
        env = FakeHarborEnv(["hello from the container"])
        bridge = HarborEnvBridge(env, asyncio.get_running_loop())
        result = await asyncio.to_thread(bridge.execute, "echo hi")
        return env, result

    env, result = asyncio.run(scenario())
    assert result["output"] == "hello from the container"
    assert result["returncode"] == 0
    assert env.calls == [("echo hi", "/workspace")]


def test_bridge_merges_stderr_into_the_observation():
    async def scenario():
        class Env:
            async def exec(self, command, **kwargs):
                return ExecResult(stdout="out", stderr="err", return_code=2)

        bridge = HarborEnvBridge(Env(), asyncio.get_running_loop())
        return await asyncio.to_thread(bridge.execute, "boom")

    result = asyncio.run(scenario())
    assert "out" in result["output"] and "err" in result["output"]
    assert result["returncode"] == 2


# --- full trial -----------------------------------------------------------

def _run_agent(tmp_path, script, outputs, spec, resume_pushback=None):
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps(spec))
    model = ScriptedModel(script)
    cls = build_agent_class()
    agent = cls(
        tmp_path / "logs",
        model_name="scripted",
        spec_path=str(spec_file),
        model_factory=lambda: model,
    )
    env = FakeHarborEnv(outputs)
    context = AgentContext()

    async def scenario():
        await agent.run("Which code path handles dedup?", env, context)
        if resume_pushback is not None:
            await agent.resume(resume_pushback, env, context)

    asyncio.run(scenario())
    return agent, env, context


def test_run_drives_mini_through_harbor_and_writes_artifacts(tmp_path):
    no_handback = {k: v for k, v in F10.items() if k != "handback"}
    agent, env, context = _run_agent(
        tmp_path,
        [("Looking.", "grep -rn dedupe_rows src/"),
         (_report("collapse_window; key (tenant_id, event_uuid)"), None), DONE],
        ["src/util/hashing.py:16:def dedupe_rows"],
        no_handback,
    )
    logs = tmp_path / "logs"
    assert (logs / "report.md").exists()
    assert "collapse_window" in (logs / "report.md").read_text()
    trajectory = json.loads((logs / "trajectory.json").read_text())
    # A real DefaultAgent keeps no `trajectory` attribute -- it must be derived
    # from `messages`, or fabrication scoring silently degrades to None.
    assert trajectory, "trajectory must be recovered from mini's messages"
    assert trajectory[0]["command"] == "grep -rn dedupe_rows src/"
    assert "dedupe_rows" in trajectory[0]["output"]
    assert env.calls, "the agent must have reached the environment"


def test_context_is_populated_for_harbor(tmp_path):
    no_handback = {k: v for k, v in F10.items() if k != "handback"}
    _, _, context = _run_agent(
        tmp_path,
        [("Looking.", "ls"), (_report("found it"), None), DONE],
        ["x"],
        no_handback,
    )
    assert context.n_input_tokens
    assert context.metadata["handoff_task_id"] == F10["id"]
    assert context.metadata["handoff_report_present"] is True
    assert context.metadata["handoff_tokens_exact"] is False  # estimated locally


def test_f10_handback_runs_inside_a_single_harbor_run(tmp_path):
    """The whole two-turn exchange, without Harbor driving a second turn."""
    agent, _, _ = _run_agent(
        tmp_path,
        [("Looking.", "grep -rn dedupe_rows src/"),
         (_report("collapse_window; key (tenant_id, event_uuid)"), None), DONE,
         ("Rechecking.", "grep -rn dedupe_rows src/ tests/"),
         (_report("Rechecked: dedupe_rows has no importers. Still collapse_window."), None), DONE],
        ["src/util/hashing.py:16:def dedupe_rows"] * 2,
        F10,
    )
    handback_log = json.loads((tmp_path / "logs" / "handback.json").read_text())
    assert "no importers" in handback_log["final_report"]
    assert handback_log["steps_after"] > 0


def test_populate_context_marks_a_missing_report(tmp_path):
    from scorers.episode import Episode, Usage

    context = populate_context(AgentContext(), Episode("t", "F2", "   ", usage=Usage(1, 1)))
    assert context.metadata["handoff_report_present"] is False


def test_fabrication_is_caught_on_a_real_agents_trajectory(tmp_path):
    """The derived trajectory must actually work as evidence, not just exist.

    This is the regression guard for the fail-open bug: with an empty
    trajectory, unsupported_claim_rate returns None and a fabricating subagent
    scores the same as an honest one.
    """
    from consumer.replay import ReplayConsumer
    from harness import artifacts
    from scorers.aggregate import score_episode

    no_handback = {k: v for k, v in F10.items() if k != "handback"}
    fabricated = "The dedup path is src/cache/bloom.py:77, keyed on a rolling hash."
    _run_agent(
        tmp_path,
        [("Looking.", "grep -rn dedupe_rows src/"), (_report(fabricated), None), DONE],
        ["src/util/hashing.py:16:def dedupe_rows"],
        no_handback,
    )
    episode = artifacts.read(tmp_path / "logs")
    consumer = ReplayConsumer({episode.report.strip(): [
        ("src/util/hashing.py::dedupe_rows", 0.9),
        ("event_uuid only", 0.9),
        ("no", 0.8),
    ]})
    row = score_episode(episode, no_handback, consumer)

    assert row["unsupported_claim_rate"] == 1.0
    assert row["unsupported_citations"] == ["src/cache/bloom.py:77"]
    assert row["decision_yield"] == 0.0
