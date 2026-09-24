"""Orchestrator track: the reference harness, metrics, ATIF import, Harbor agent.

Harness tests drive the real mini-swe-agent loop with scripted policies (no
key), so caps, `subagent` interception and threading are the real thing. The
rehearsal assertions are the claims ORCHESTRATOR.md makes about metric shapes:
solo hits a wall, judicious delegation clears it, eager delegation pays a tax
on coupled work, and sloppy delegation shows up in the process diagnostics.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch.atif import telemetry_from_atif  # noqa: E402
from orch.families import coupled, probe, small, wide  # noqa: E402
from orch.harness import (  # noqa: E402
    SubagentSyntaxError,
    is_subagent_command,
    parse_subagent_command,
    truncate,
)
from orch.metrics import coverage_and_duplication, summarise, synthesis_loss  # noqa: E402

# --- the subagent command ---------------------------------------------------------------


def test_parse_heredoc_spawns_and_wait():
    ops = parse_subagent_command(
        "subagent spawn <<'EOF'\nread tickets/T-1.txt\nand T-2\nEOF\n"
        "subagent spawn <<EOF\nsecond\nEOF\nsubagent wait a1 a2"
    )
    assert ops == [("spawn", "read tickets/T-1.txt\nand T-2"), ("spawn", "second"),
                   ("wait", ["a1", "a2"])]


def test_parse_inline_run_and_bare_wait():
    assert parse_subagent_command('subagent run "check the logs"') == [("run", "check the logs")]
    assert parse_subagent_command("subagent wait") == [("wait", [])]


@pytest.mark.parametrize("command", [
    "subagent spawn <<'EOF'\nno terminator",
    "subagent spawn <<'EOF'\nEOF",
    "subagent spawn <<'EOF'\nx\nEOF\nls -la",
    "subagent frobnicate",
])
def test_parse_rejects_anything_else(command):
    with pytest.raises(SubagentSyntaxError):
        parse_subagent_command(command)


def test_only_a_leading_subagent_is_intercepted():
    assert is_subagent_command("\n  subagent wait")
    assert not is_subagent_command("cd x && subagent wait")
    assert not is_subagent_command("echo subagent")


def test_truncate_keeps_head_and_tail():
    text = "A" * 100 + "B" * 100
    out = truncate(text, 60)
    assert out.startswith("A" * 40) and out.endswith("B" * 20) and "truncated" in out
    assert truncate("short", 60) == "short"


# --- the harness, driven by scripted policies --------------------------------------------

mini = pytest.importorskip("minisweagent.agents.default")

from orch import policies  # noqa: E402
from orch.local import run_local  # noqa: E402


def _run(task, system, tmp_path, **kw):
    mode, lead, worker_factory = policies.build(system, task)
    cond = f"delegate:{system}" if mode == "delegate" else mode
    return run_local(task, mode, lead, worker_factory, out_dir=tmp_path / f"{task.id}-{system}",
                     system="t", condition=cond, **kw)


def test_solo_hits_the_context_wall_on_wide_and_delegation_clears_it(tmp_path):
    task = wide.generate(72, 1)
    solo = _run(task, "solo", tmp_path)
    assert solo["telemetry"]["lead"]["exit_status"] == "ContextExceeded"
    assert solo["telemetry"]["lead"]["context_peak"] > task.limits["context_tokens"]
    assert 0 < solo["reward"]["reward"] < 1.0, "writing as it goes preserves partial credit"
    judicious = _run(task, "judicious", tmp_path)
    assert judicious["reward"]["reward"] == 1.0
    tel = judicious["telemetry"]
    assert len(tel["workers"]) == 8
    assert all(w["context_peak"] <= task.limits["context_tokens"] for w in tel["workers"])
    assert tel["lead"]["context_peak"] < task.limits["context_tokens"] // 4


def test_solo_hits_the_step_wall_on_probes(tmp_path):
    task = probe.generate(20, 1)
    solo = _run(task, "solo", tmp_path)
    assert solo["telemetry"]["lead"]["exit_status"] == "StepLimitExceeded"
    assert solo["reward"]["reward"] < 1.0
    assert _run(task, "judicious", tmp_path)["reward"]["reward"] == 1.0


def test_solo_xl_scales_limits_for_the_lead(tmp_path):
    task = wide.generate(72, 1)
    record = _run(task, "solo-xl", tmp_path)
    assert record["reward"]["reward"] == 1.0
    assert record["telemetry"]["limits"]["context_tokens"] == 8 * task.limits["context_tokens"]


def test_oracle_split_uses_the_ideal_partition(tmp_path):
    task = probe.generate(10, 1)
    record = _run(task, "oracle-split", tmp_path)
    assert record["reward"]["reward"] == 1.0
    assert [w["brief"] for w in record["telemetry"]["workers"]] == \
        [p["brief"] for p in task.oracle_plan]


def test_oracle_split_is_solo_where_delegating_does_not_pay(tmp_path):
    record = _run(small.generate(1, 1), "oracle-split", tmp_path)
    assert record["telemetry"]["oracle_is_solo"] and not record["telemetry"]["workers"]


def test_eager_fan_out_breaks_the_coupled_change(tmp_path):
    task = coupled.generate(7, 1)
    assert _run(task, "solo", tmp_path)["reward"]["reward"] == 1.0
    eager = _run(task, "eager", tmp_path)
    assert len(eager["telemetry"]["workers"]) == 7
    assert eager["reward"]["reward"] < 1.0


def test_workers_cannot_spawn_and_solo_has_no_subagent_command(tmp_path):
    from minisweagent.environments.local import LocalEnvironment

    from orch.harness import DelegatingEnv, Limits, SubagentPool

    env = LocalEnvironment(cwd=str(tmp_path))
    solo = DelegatingEnv(env, Limits(), pool=None)
    assert solo.execute({"command": "subagent wait"})["returncode"] == 127
    pool = SubagentPool(env, lambda: None, Limits(max_total_subagents=0), lambda *a: None)
    lead = DelegatingEnv(env, Limits(), pool=pool)
    assert "limit" in lead.execute({"command": "subagent spawn <<'E'\nx\nE"})["output"]
    bad = lead.execute({"command": "subagent spawn <<'E'\nx\nE\nls"})
    assert bad["returncode"] == 2


def test_every_observation_carries_a_usage_footer(tmp_path):
    record = _run(small.generate(1, 1), "solo", tmp_path)
    trajectories = json.loads((tmp_path / f"{record['task_id']}-solo" / "logs" /
                               "trajectories.json").read_text())
    observations = [m["content"] for m in trajectories["lead"] if m["role"] == "user"][1:]
    assert observations and all("[context:" in o for o in observations)


# --- metrics --------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rehearsal(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("rehearsal")
    tasks = [wide.generate(6, 1), wide.generate(72, 1), probe.generate(20, 1),
             coupled.generate(4, 1), small.generate(1, 1)]
    records = []
    for task in tasks:
        for system in ("solo", "solo-xl", "oracle-split", "judicious", "eager", "sloppy"):
            records.append(_run(task, system, tmp))
    return summarise(records)


def test_rehearsal_metric_shapes(rehearsal):
    summary, _ = rehearsal
    judicious = summary[("t", "delegate:judicious")]
    eager = summary[("t", "delegate:eager")]
    sloppy = summary[("t", "delegate:sloppy")]
    assert judicious["capture"] == pytest.approx(1.0)
    assert judicious["mean_tax"] == 0 and judicious["decision_balanced_acc"] == 1.0
    assert eager["mean_tax"] > 0 and eager["decision_balanced_acc"] == 0.5
    assert sloppy["capture"] < 0.5
    assert sloppy["coverage"] < 1.0 and sloppy["duplication"] > 0 and sloppy["synthesis_loss"] > 0
    for cell in judicious["cells"]:
        # a perfect reader has no context rot: solo-xl ties delegate, and the
        # structural-lift column must say so rather than invent a benefit
        assert cell["structural_lift"] == pytest.approx(0.0)


def test_capture_is_undefined_where_there_is_no_gap(rehearsal):
    summary, _ = rehearsal
    small_cells = [c for c in summary[("t", "delegate:judicious")]["cells"] if c["size"] == 6]
    assert small_cells and small_cells[0]["capture"] is None


def test_coverage_and_duplication_match_item_mentions():
    tel = {"workers": [{"brief": "tickets/T-1.txt tickets/T-2.txt"},
                       {"brief": "tickets/T-2.txt"}]}
    coverage, dup = coverage_and_duplication(tel, ["T-1", "T-2", "T-3", "T-10"])
    assert coverage == 0.5 and dup == 0.5


def test_synthesis_loss_counts_findings_dropped_by_the_lead():
    record = {
        "family": "W",
        "truth": {"matches": [{"ticket": "T-1", "order": "O-1"}, {"ticket": "T-2", "order": "O-2"}]},
        "telemetry": {"workers": [{"report": '{"ticket": "T-1", "order": "O-1"}\n'
                                             '{"ticket": "T-2", "order": "O-2"}'}]},
        "answer": {"matches": [{"ticket": "T-1", "order": "O-1"}]},
    }
    assert synthesis_loss(record) == 0.5


# --- ATIF import ------------------------------------------------------------------------------

def _atif():
    return {
        "schema_version": "ATIF-v1.6",
        "session_id": "s1",
        "agent": {"name": "claude-code", "version": "2.1", "model_name": "claude-sonnet-5"},
        "steps": [
            {"step_id": 1, "source": "user", "message": "task",
             "timestamp": "2026-09-24T00:00:00Z"},
            {"step_id": 2, "source": "agent", "message": "fanning out",
             "timestamp": "2026-09-24T00:00:05Z",
             "metrics": {"prompt_tokens": 3000, "completion_tokens": 200},
             "tool_calls": [
                 {"tool_call_id": "c1", "function_name": "Agent",
                  "arguments": {"prompt": "read tickets/T-1.txt", "description": "batch 1"}},
                 {"tool_call_id": "c2", "function_name": "Agent",
                  "arguments": {"prompt": "read tickets/T-2.txt", "description": "batch 2"}},
             ],
             "observation": {"results": [
                 {"source_call_id": "c1", "content": '{"ticket": "T-1", "order": "O-1"}'},
                 {"source_call_id": "c2", "content": "none"},
             ]}},
            {"step_id": 3, "source": "agent", "message": "reading",
             "timestamp": "2026-09-24T00:00:07Z", "extra": {"is_sidechain": True},
             "metrics": {"prompt_tokens": 1500, "completion_tokens": 50}},
            {"step_id": 4, "source": "agent", "message": "done",
             "timestamp": "2026-09-24T00:00:30Z",
             "metrics": {"prompt_tokens": 4000, "completion_tokens": 100}},
        ],
    }


def test_atif_fixture_is_valid_atif():
    trajectory = pytest.importorskip("harbor.models.trajectories.trajectory")
    trajectory.Trajectory.model_validate(_atif())


def test_atif_spawns_become_workers_with_briefs_and_reports():
    tel = telemetry_from_atif(_atif(), "orch-w-n6-s1", "W")
    assert [w["brief"] for w in tel["workers"]] == ["read tickets/T-1.txt", "read tickets/T-2.txt"]
    assert tel["workers"][0]["report"].startswith('{"ticket"')
    assert tel["lead"]["context_peak"] == 4000 and tel["lead"]["input_tokens"] == 7000
    assert tel["unattributed_worker_tokens"]["input_tokens"] == 1500
    assert tel["wall_clock_sec"] == 30 and tel["tokens_exact"]


def test_atif_solo_run_has_no_workers():
    traj = _atif()
    traj["steps"] = [s for s in traj["steps"] if not s.get("tool_calls")]
    assert telemetry_from_atif(traj)["workers"] == []


# --- Harbor agent ---------------------------------------------------------------------------------

def test_harbor_agent_classes_satisfy_the_real_interface(tmp_path):
    pytest.importorskip("harbor")
    from orch.harbor_agent import build_agent_class, build_rehearsal_class

    for cls in (build_agent_class(), build_rehearsal_class()):
        assert cls.__abstractmethods__ == frozenset()
    agent = build_agent_class()(tmp_path, model_name="anthropic/x", mode="solo", context_tokens=1000)
    assert agent.options.mode == "solo" and agent.options.context_tokens == 1000


def test_harbor_agent_runs_delegation_through_the_async_bridge(tmp_path, monkeypatch):
    """The real Harbor agent class, a fake async environment, parallel workers."""
    pytest.importorskip("harbor")
    from harbor.environments.base import ExecResult
    from harbor.models.agent.context import AgentContext

    from orch.emit import emit
    from orch.harbor_agent import build_rehearsal_class
    from orch.local import materialise

    task = wide.generate(24, 1)
    emit(task, tmp_path / "tasks" / task.id)
    ws, _, _ = materialise(task, tmp_path / "run")
    monkeypatch.setenv("ORCH_REHEARSAL_TASKS", str(tmp_path / "tasks"))

    class SubprocessEnv:
        async def exec(self, command, cwd=None, env=None, timeout_sec=None, user=None):
            proc = await asyncio.create_subprocess_shell(
                command, cwd=ws, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = await proc.communicate()
            return ExecResult(stdout=out.decode(), stderr=err.decode(), return_code=proc.returncode)

    agent = build_rehearsal_class()(tmp_path / "logs", model_name="scripted", system="judicious")
    context = AgentContext()
    asyncio.run(agent.run(task.instruction, SubprocessEnv(), context))
    tel = json.loads((tmp_path / "logs" / "telemetry.json").read_text())
    assert len(tel["workers"]) == 3 and all(w["exit_status"] == "Submitted" for w in tel["workers"])
    assert context.metadata["orch_subagents"] == 3
    answer = json.loads((ws / "answer.json").read_text())
    assert {m["ticket"] for m in answer["matches"]} == {m["ticket"] for m in task.truth["matches"]}
    assert os.path.exists(tmp_path / "logs" / "trajectories.json")


def test_collect_detects_conditions_from_job_config():
    sys.path.insert(0, str(ROOT / "tools"))
    from orch_collect import detect

    cc = {"agent": {"name": "claude-code", "model_name": "anthropic/m",
                    "kwargs": {"disallowed_tools": "Agent,Task"}}}
    assert detect(cc) == ("claude-code/anthropic/m", "solo")
    cc["agent"]["kwargs"] = {}
    assert detect(cc)[1] == "delegate"
    ref = {"agent": {"name": "orch.harbor_agent:OrchMiniAgent", "kwargs": {"mode": "solo-xl"}}}
    assert detect(ref) == ("OrchMiniAgent", "solo-xl")
