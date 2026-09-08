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
        try:
            agent.step()
        except Exception as exc:  # noqa: BLE001 - re-raised unless it carries messages
            # mini raises InterruptAgentFlow (and its LimitsExceeded /
            # FormatError subclasses) to end or redirect a turn, carrying the
            # messages to append. Duck-typed so this needs no mini import.
            carried = getattr(exc, "messages", None)
            if carried is None:
                raise
            add = getattr(agent, "add_messages", None)
            if add is not None:
                add(*carried)
            else:
                agent.messages.extend(carried)
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


def resume_with(agent, pushback_message, max_steps=200):
    """Deliver the pushback to an agent that has already exited, and step on.

    mini's `run()` resets `messages` and loops to exit, so a second `run()` would
    throw the first turn away. Resuming instead means appending to the history it
    left behind -- which works because that history is a plain list.

    The exit marker is lifted out first: it is mini's internal terminator, not a
    conversational turn to show a model.
    """
    if not at_exit(agent):
        raise ValueError("agent has not exited; nothing to resume from")
    first_report = extract_report(_final_text(agent))
    exit_marker = agent.messages.pop()
    message = {"role": "user", "content": render_handback(pushback_message)}
    if hasattr(agent, "add_messages"):
        agent.add_messages(message)
    else:
        agent.messages.append(message)
    steps_after = run_to_exit(agent, max_steps)
    return first_report, exit_marker, steps_after


def play(agent, pushback_message, max_steps=200, start=None):
    """Run the first turn, deliver the scripted pushback, run the second.

    `start` runs turn one. For a real mini agent that is `agent.run(task=...)`,
    which initialises the history from the templates; the default just steps,
    which suits an agent whose history is already primed.
    """
    if start is not None:
        start()
        steps_before = 0
    else:
        steps_before = run_to_exit(agent, max_steps)

    first_report, exit_marker, steps_after = resume_with(
        agent, pushback_message, max_steps
    )

    return HandbackResult(
        first_report=first_report,
        final_report=extract_report(_final_text(agent)),
        pushback=pushback_message,
        steps_before=steps_before,
        steps_after=steps_after,
        messages=list(agent.messages) + [exit_marker],
    )
