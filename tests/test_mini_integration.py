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
        # Real mini v2 emits action dicts, not bare strings.
        actions = [{"command": action}] if action else []
        return {"role": "assistant", "content": text, "extra": {"actions": actions}}

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
        self.executed.append(action.get("command") if isinstance(action, dict) else action)
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


# --- the real tool-calling model --------------------------------------------
#
# The scripted model above hands DefaultAgent ready-made action dicts, so it
# never exercises mini's own response parsing -- which is where the first real
# Milestone 1 run broke: LitellmModel raises FormatError on any reply without a
# tool call, discarding the text. A final report IS such a reply. These tests
# drive the real LitellmModel with litellm.completion stubbed out.

litellm = pytest.importorskip("litellm")


def _tool_reply(command, call_id):
    return litellm.ModelResponse(choices=[{
        "message": {"role": "assistant", "content": "Checking.", "tool_calls": [{
            "id": call_id, "type": "function",
            "function": {"name": "bash", "arguments": f'{{"command": "{command}"}}'},
        }]},
        "finish_reason": "tool_calls",
    }])


def _text_reply(text):
    return litellm.ModelResponse(choices=[{
        "message": {"role": "assistant", "content": text}, "finish_reason": "stop",
    }])


class ToolEnv(ScriptedEnv):
    """Outputs shaped like LocalEnvironment's, which mini's observation template reads."""

    def execute(self, action, **kwargs):
        return {**super().execute(action, **kwargs), "exception_info": ""}


def _real_model_agent(monkeypatch, replies, outputs):
    from minisweagent.models.litellm_model import LitellmModel

    queue = list(replies)
    monkeypatch.setattr(litellm, "completion", lambda **kw: queue.pop(0))
    model = LitellmModel(model_name="claude-test", cost_tracking="ignore_errors")
    return build_mini_agent(model, ToolEnv(outputs), step_limit=10)


def test_real_model_final_report_ends_the_episode(monkeypatch):
    agent = _real_model_agent(
        monkeypatch,
        [_tool_reply("ls config", "call_1"),
         _text_reply("Done.\n" + _report("config/app.yaml does not exist"))],
        ["ls: cannot access 'config': No such file or directory"],
    )
    agent.run(task="t", budget_tokens=100)

    assert agent.messages[-1]["role"] == "exit"
    assert agent.messages[-1]["extra"]["exit_status"] == "Submitted"
    assert handback._final_text(agent).endswith(REPORT_CLOSE)
    assert "config/app.yaml does not exist" in agent.messages[-1]["content"]


def test_real_model_reply_without_tool_or_report_is_nudged(monkeypatch):
    agent = _real_model_agent(
        monkeypatch,
        [_text_reply("Let me think."), _text_reply(_report("ok"))], [],
    )
    agent.run(task="t", budget_tokens=100)
    nudges = [m for m in agent.messages if m.get("extra", {}).get("interrupt_type") == "FormatError"]
    assert len(nudges) == 1 and REPORT_OPEN in nudges[0]["content"]
    assert agent.messages[-1]["extra"]["exit_status"] == "Submitted"


def test_real_model_trajectory_pairs_each_command_with_its_own_output(monkeypatch):
    from harness.episode_runner import trajectory_from_messages

    agent = _real_model_agent(
        monkeypatch,
        [_tool_reply("ls", "call_1"), _tool_reply("cat a", "call_2"), _text_reply(_report("r"))],
        ["LS_OUTPUT", "CAT_OUTPUT"],
    )
    agent.run(task="t", budget_tokens=100)
    steps = trajectory_from_messages(agent.messages)
    assert [s["command"] for s in steps] == ["ls", "cat a"]
    assert "LS_OUTPUT" in steps[0]["output"] and "CAT_OUTPUT" in steps[1]["output"]


def test_real_model_handback_resumes_after_a_text_report(monkeypatch):
    agent = _real_model_agent(
        monkeypatch,
        [_tool_reply("grep -rn dedupe_rows src/", "call_1"),
         _text_reply(_report("collapse_window")),
         _tool_reply("grep -rn dedupe_rows src/ tests/", "call_2"),
         _text_reply(_report("Rechecked: still collapse_window"))],
        ["src/util/hashing.py:16:def dedupe_rows", "src/util/hashing.py:16:def dedupe_rows"],
    )
    result = handback.play(agent, "dedupe_rows is the path.",
                           start=lambda: agent.run(task="t", budget_tokens=100))
    assert result.first_report == "collapse_window"
    assert result.final_report == "Rechecked: still collapse_window"
    # The API rejects a tool_use without a tool_result; the report turn has none.
    assert all(not m.get("tool_calls") for m in agent.messages
               if m.get("role") == "assistant" and REPORT_OPEN in str(m.get("content")))
