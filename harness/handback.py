"""F10's scripted handback, played inside a single trial.

Harbor runs one `run()` per trial and mini-swe-agent cannot resume past its exit
message, which looked like a blocker for the handback turn. It is not: the
pushback is *scripted* -- it lives in the task spec, not in a live orchestrator
-- so the wrapper can deliver it itself. The two-turn exchange happens entirely
inside one trial and needs nothing from either dependency (DESIGN.md 8.1).

The only assumption made about the agent is mini's own shape: a linear
`messages` list, and a `step()` that appends to it until a message with role
"exit" lands.
"""

from dataclasses import dataclass, field

from harness.templates import extract_report, render_handback

EXIT_ROLE = "exit"


class AgentStalled(Exception):
    """The agent ran past its step ceiling without exiting."""


def at_exit(agent):
    return bool(agent.messages) and agent.messages[-1].get("role") == EXIT_ROLE


def run_to_exit(agent, max_steps=200):
    """Step until the agent exits. Returns the number of steps taken."""
    steps = 0
    while not at_exit(agent):
        if steps >= max_steps:
            raise AgentStalled(f"no exit after {max_steps} steps")
        agent.step()
        steps += 1
    return steps


def _final_text(agent):
    """Text of the last assistant turn before the exit marker."""
    for message in reversed(agent.messages):
        if message.get("role") == "assistant":
            return message.get("content", "")
    return ""


@dataclass
class HandbackResult:
    first_report: str
    final_report: str
    pushback: str
    steps_before: int = 0
    steps_after: int = 0
    messages: list = field(default_factory=list)

    @property
    def report_changed(self):
        """Did the report text change after the pushback?

        Descriptive only. A subagent that holds its ground but adds the evidence
        it was asked for also changes its text, so this does not say whether it
        capitulated -- the decision probe does (DESIGN.md 6, F10).
        """
        return self.first_report.strip() != self.final_report.strip()


def play(agent, pushback_message, max_steps=200):
    """Run the agent, deliver the scripted pushback, run it again.

    The exit marker is lifted out of the history before the pushback is
    appended: it is mini's internal terminator, not something to show a model.
    """
    steps_before = run_to_exit(agent, max_steps)
    first_report = extract_report(_final_text(agent))

    exit_marker = agent.messages.pop()
    agent.messages.append(
        {"role": "user", "content": render_handback(pushback_message)}
    )
    steps_after = run_to_exit(agent, max_steps)

    return HandbackResult(
        first_report=first_report,
        final_report=extract_report(_final_text(agent)),
        pushback=pushback_message,
        steps_before=steps_before,
        steps_after=steps_after,
        messages=list(agent.messages) + [exit_marker],
    )
