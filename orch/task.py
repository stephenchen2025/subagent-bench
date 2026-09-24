"""A generated orchestrator-track task, before it is rendered for any runner.

A task is data: the files the agent sees, the tools installed beside them, the
ground truth only the verifier sees, and an oracle solution that proves the task
is solvable. `orch.emit` renders it as a Harbor task directory; the reference
harness can also materialise it into a temp dir and run it with no container.
"""

import random
from dataclasses import dataclass, field

# How a task is labelled for the delegation-judgment metric (ORCHESTRATOR.md 5.3).
DELEGATE = "delegate"   # a solo agent hits a per-agent wall; delegating should pay
OPTIONAL = "optional"   # small enough that either policy can succeed
SOLO = "solo"           # delegating costs more than it returns
LABELS = (DELEGATE, OPTIONAL, SOLO)

# Reference-harness limits (ORCHESTRATOR.md 6). Identical for the lead and for
# every worker; the experiment varies only whether workers exist.
DEFAULT_LIMITS = {
    "context_tokens": 32_000,
    "step_limit": 160,
    "observation_chars": 16_000,
    "max_concurrent_subagents": 8,
    "max_total_subagents": 16,
}


@dataclass
class OrchTask:
    id: str
    family: str
    size: int
    seed: int
    label: str
    instruction: str
    # workspace-relative path -> text. Rendered into /workspace.
    files: dict
    # ground truth; lives only in the verifier's tests/ dir.
    truth: dict
    # bash body of solution/solve.sh -- the oracle, which must score 1.0.
    solution: str
    # ids of the independent units of work (tickets, services). Coverage and
    # duplication in a delegate run are measured against these.
    work_items: list = field(default_factory=list)
    # ideal decomposition for the oracle-split condition: [{"brief", "items"}].
    oracle_plan: list = field(default_factory=list)
    # absolute image path -> text, for tools installed outside the workspace.
    tool_files: dict = field(default_factory=dict)
    # hidden test files for code families: tests/-relative path -> text.
    hidden_tests: dict = field(default_factory=dict)
    limits: dict = field(default_factory=lambda: dict(DEFAULT_LIMITS))
    env: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.label not in LABELS:
            raise ValueError(f"unknown label {self.label!r}")


def rng_for(family, size, seed):
    """One RNG per (family, size, seed): tasks are reproducible from their id."""
    return random.Random(f"{family}:{size}:{seed}")


def task_id(family, size, seed):
    return f"orch-{family.lower()}-n{size}-s{seed}"


def approx_tokens(text):
    """The same char/4 estimate the reference harness uses for its caps."""
    return max(1, len(text) // 4)
