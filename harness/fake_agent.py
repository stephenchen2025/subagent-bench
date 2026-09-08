"""A scripted stand-in for mini-swe-agent, for testing the harness offline.

Mimics only what the harness relies on: a linear `messages` list and a `step()`
that appends until an exit message lands.
"""

from harness.handback import EXIT_ROLE


class FakeMiniAgent:
    """Replays a scripted sequence of assistant turns.

    Each script entry is either a string (an assistant turn, after which an
    observation is appended) or the sentinel EXIT, which terminates the run.
    """

    EXIT = object()

    def __init__(self, script, observations=None):
        self._script = list(script)
        self._observations = list(observations or [])
        self.messages = []
        self.trajectory = []

    def step(self):
        if not self._script:
            raise RuntimeError("script exhausted before exit")
        item = self._script.pop(0)
        if item is self.EXIT:
            self.messages.append({"role": EXIT_ROLE, "content": "", "extra": {}})
            return
        self.messages.append({"role": "assistant", "content": item})
        observation = (
            self._observations.pop(0) if self._observations else "(no output)"
        )
        self.messages.append({"role": "user", "content": observation})
        self.trajectory.append({"command": item, "output": observation})
