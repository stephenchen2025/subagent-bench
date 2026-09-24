"""Drive one delegation episode and leave the artifacts behind.

Kept free of any Harbor or mini-swe-agent import so it can be exercised offline
against a scripted agent. `harness/agent.py` is the thin shim that hands the
real ones to it.
"""

from harness import artifacts, handback
from harness.budget import TokenBudget
from harness.templates import extract_report
from scorers.episode import Episode, Usage


def _final_assistant_text(agent):
    for message in reversed(agent.messages):
        if message.get("role") == "assistant":
            return message.get("content", "")
    return ""


def trajectory_from_messages(messages):
    """Recover the command/observation record from mini's linear history.

    The real DefaultAgent keeps no `trajectory` attribute -- `messages` is the
    record. Deriving from it matters more than it looks: an empty trajectory
    makes fabrication detection and calibration return None rather than fail, so
    getting this wrong would silently switch off the axes that need it.
    """
    steps = []
    for i, message in enumerate(messages):
        if message.get("role") != "assistant":
            continue
        actions = (message.get("extra") or {}).get("actions") or []
        # Tool-calling mini returns one role="tool" message per action, keyed by
        # tool_call_id; text-based mini returns a single role="user" message.
        observation = ""
        by_call_id = {}
        for later in messages[i + 1:]:
            role = later.get("role")
            if role == "tool":
                by_call_id[later.get("tool_call_id")] = str(later.get("content", ""))
                continue
            if role == "user" and not by_call_id:
                observation = str(later.get("content", ""))
            break
        tool_outputs = list(by_call_id.values())
        for n, action in enumerate(actions or [None]):
            command = (
                action.get("command", "") if isinstance(action, dict)
                else str(action or "")
            )
            output = observation
            if by_call_id:
                call_id = action.get("tool_call_id") if isinstance(action, dict) else None
                output = by_call_id.get(call_id, tool_outputs[n] if n < len(tool_outputs) else "")
            if not command and not output:
                continue
            steps.append({"command": command, "output": output})
    return steps


def _trajectory(agent):
    explicit = getattr(agent, "trajectory", None)
    if explicit:
        return list(explicit)
    return trajectory_from_messages(getattr(agent, "messages", []) or [])


def _charge(budget, agent):
    """Charge every message the agent produced or read against the cap."""
    for message in agent.messages:
        content = message.get("content")
        if isinstance(content, str) and content:
            budget.charge(content)
    return budget


def run_episode(agent, spec, counter, logs_dir=None, max_steps=200, start=None):
    """Run the agent over one task spec; return (Episode, HandbackResult|None).

    An F10 spec carries a scripted pushback, so the two-turn exchange happens
    here, inside a single trial. Nothing about it needs framework support: the
    orchestrator's line is in the spec, not on a wire.
    """
    budget = TokenBudget(spec["budget"]["max_tokens"], counter)
    pushback = (spec.get("handback") or {}).get("message")

    if pushback:
        result = handback.play(agent, pushback, max_steps=max_steps, start=start)
        report = result.final_report
        steps = result.steps_before + result.steps_after
    else:
        result = None
        if start is not None:
            start()
            steps = 0
        else:
            steps = handback.run_to_exit(agent, max_steps=max_steps)
        report = extract_report(_final_assistant_text(agent))

    _charge(budget, agent)
    snap = budget.snapshot()

    episode = Episode(
        task_id=spec["id"],
        family=spec["family"],
        report=report,
        trajectory=_trajectory(agent),
        effects={},  # filled by the in-trial verifier
        usage=Usage(input_tokens=snap["spent_tokens"], tool_calls=steps),
        budget_tokens=spec["budget"]["max_tokens"],
        reference_tokens=spec["budget"].get("reference_tokens", 0),
        returned_early=not snap["over_budget"] and budget.remaining > 0,
    )
    episode.tokens_exact = snap["tokens_exact"]

    if logs_dir is not None:
        artifacts.write(logs_dir, episode, result)
    return episode, result


def missing_report(episode):
    """An agent that never produced a delimited report.

    Not scored as a bad report -- scored as a failed trial, and reported as one.
    A silently empty report would otherwise look like a very terse subagent.
    """
    return not episode.report.strip()
