"""The episode record: what one delegation trial produces (DESIGN.md 8.2)."""

from dataclasses import dataclass, field


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    wall_clock_s: float = 0.0

    @property
    def total_tokens(self):
        return self.input_tokens + self.output_tokens


@dataclass
class Episode:
    """One subagent run over one task.

    `trajectory` is the flat list of steps the agent actually took, each with the
    command issued and the output observed. It is required for fidelity and
    calibration; a system that cannot produce it is scored on the other axes and
    marked as such.
    """

    task_id: str
    family: str
    report: str
    trajectory: list[dict] = field(default_factory=list)
    effects: dict = field(default_factory=dict)
    usage: Usage = field(default_factory=Usage)
    budget_tokens: int = 0
    reference_tokens: int = 0
    returned_early: bool = False

    @property
    def has_trajectory(self):
        return bool(self.trajectory)

    def observed_text(self):
        """Everything the subagent actually saw. The evidence base for 5.2."""
        parts = []
        for step in self.trajectory:
            parts.append(str(step.get("command", "")))
            parts.append(str(step.get("output", "")))
        return "\n".join(parts)

    def over_budget(self):
        return bool(self.budget_tokens) and self.usage.total_tokens > self.budget_tokens
