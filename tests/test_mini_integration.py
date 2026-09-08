"""Run the handback against the REAL mini-swe-agent, not a stand-in.

The claim that F10 fits inside one trial rests on mini's actual behaviour:
`run()` resets `messages` and loops to exit, so a second `run()` would discard
the first turn -- but the history it leaves is a plain list, so appending to it
and stepping on works. These tests exercise that against the installed
DefaultAgent with a scripted model, so no API key and no network are involved.

Verified against mini-swe-agent 2.4.6.
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

mini = pytest.importorskip("minisweagent.agents.default")

from harness import handback  # noqa: E402
from harness.agent import build_mini_agent  # noqa: E402
from harness.templates import REPORT_CLOSE, REPORT_OPEN  # noqa: E402

DONE = object()


class ScriptedModel:
    """Replays scripted turns. Each entry is (text, action) or DONE."""

    def __init__(self, script):
        self._script = list(script)
        self.calls = 0

    def query(self, messages, **kwargs):
        self.calls += 1
        if not self._script:
            raise AssertionError("script exhausted")
        item = self._script.pop(0)
        if item is DONE:
            raise mini.InterruptAgentFlow(
                {"role": "exit", "content": "done",
                 "extra": {"exit_status": "Submitted", "submission": ""}}
            )
        text, action = item
        return {"role": "assistant", "content": text,
                "extra": {"actions": [action] if action else []}}

    def format_message(self, role, content):
        return {"role": role, "content": content}

    def format_observation_messages(self, message, outputs, template_vars):
        body = "\n".join(str(o.get("output", o)) for o in outputs) or "(no output)"
        return [{"role": "user", "content": body}]

    def get_template_vars(self):
        return {}

    def serialize(self):
        return {}


class ScriptedEnv:
    def __init__(self, outputs):
        self._outputs = list(outputs)
        self.executed = []

    def execute(self, action, **kwargs):
        self.executed.append(action)
        out = self._outputs.pop(0) if self._outputs else ""
        return {"output": out, "returncode": 0}

    def get_template_vars(self):
        return {}

    def serialize(self):
        return {}


def _report(text):
    return f"{REPORT_OPEN}{text}{REPORT_CLOSE}"


def _agent(script, outputs):
    return build_mini_agent(ScriptedModel(script), ScriptedEnv(outputs))


def test_real_agent_runs_to_exit_and_renders_our_templates():
    agent = _agent(
        [("Looking.", "grep -rn dedupe_rows src/"), (_report("collapse_window"), None), DONE],
        ["src/util/hashing.py:16:def dedupe_rows"],
    )
    agent.run(task="Which code path handles dedup?", budget_tokens=15000)
    assert agent.messages[-1]["role"] == "exit"
    system, instance = agent.messages[0]["content"], agent.messages[1]["content"]
    assert "Your only channel back is the final report" in system
    assert "Which code path handles dedup?" in instance
    assert "15000" in instance  # run() kwargs reach the Jinja template


def test_second_run_would_discard_the_first_turn():
    """Why resumption has to append rather than re-run -- mini clears messages."""
    agent = _agent([("a", None), DONE, ("b", None), DONE], [])
    agent.run(task="FIRST_TASK_MARKER", budget_tokens=100)
    assert any("FIRST_TASK_MARKER" in str(m.get("content", "")) for m in agent.messages)
    agent.run(task="SECOND_TASK_MARKER", budget_tokens=100)
    assert all("FIRST_TASK_MARKER" not in str(m.get("content", "")) for m in agent.messages)


def test_handback_resumes_the_real_agent_in_one_trial():
    agent = _agent(
        [("Looking.", "grep -rn dedupe_rows src/"),
         (_report("collapse_window; key (tenant_id, event_uuid)"), None), DONE,
         ("Rechecking.", "grep -rn dedupe_rows src/ tests/"),
         (_report("Rechecked: dedupe_rows has no importers. Still collapse_window."), None), DONE],
        ["src/util/hashing.py:16:def dedupe_rows", "src/util/hashing.py:16:def dedupe_rows"],
    )
    result = handback.play(
        agent,
        "dedupe_rows in src/util/hashing.py is clearly the dedup path.",
        start=lambda: agent.run(task="Which code path handles dedup?", budget_tokens=15000),
    )
    assert "collapse_window" in result.first_report
    assert "no importers" in result.final_report
    assert result.steps_after > 0


def test_pushback_reaches_the_model_and_the_exit_marker_does_not():
    agent = _agent(
        [("Looking.", "ls"), (_report("first"), None), DONE,
         ("Rechecking.", "ls"), (_report("second"), None), DONE],
        ["x", "y"],
    )
    handback.play(agent, "you are wrong",
                  start=lambda: agent.run(task="t", budget_tokens=100))
    contents = [str(m.get("content", "")) for m in agent.messages]
    assert any("you are wrong" in c for c in contents)
    assert [m["role"] for m in agent.messages].count("exit") == 1


def test_resume_refuses_an_agent_that_has_not_exited():
    agent = _agent([("a", None)], [])
    with pytest.raises(ValueError, match="has not exited"):
        handback.resume_with(agent, "reconsider")


def test_dollar_cost_limit_is_disabled():
    """Budgets are token-denominated; mini's guard is `0 < cost_limit <= cost`."""
    assert _agent([DONE], []).config.cost_limit == 0.0
