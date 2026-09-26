"""Why a single agent times out on these tasks and a delegating one does not.

A long-horizon task here is N independent *units* (a service to audit, a package
to migrate, a host's logs to read) plus a synthesis step. Two estimates of a
single agent's wall clock are computed, and the gate uses the harsher one:

**Careful agent.** Works unit by unit. Each unit costs
`ceil(chars / TOOL_OUTPUT_CHARS)` reads plus some judgement turns, and every
turn gets slower as context grows (each turn re-reads a longer prefix).

**Ideal batching agent -- the floor.** Reads many units per tool call, so it
pays only `ceil(total_chars / TOOL_OUTPUT_CHARS)` reads. What it cannot batch
away:

1. Everything essential still passes through its one context, at most
   TOOL_OUTPUT_CHARS per call, and past the window it compacts.
2. Every unit still needs its own reasoning and output tokens (the judgement,
   or the edit). One agent decodes those one after another; parallel
   subagents decode theirs at the same time. **This is the cost that
   delegation parallelises and batching cannot.**

A task is admitted only if even the floor exceeds the timeout, the careful
agent exceeds it by half again, and the delegated estimate -- with CAREFUL
subagents, the pessimistic case for delegation -- fits well inside it.

The unit sizes are measured from the generated workspace. The latency, decode
and output-token constants are ASSUMPTIONS. A calibration run replaces them
(longhorizon/README.md, "Admission gate: the empirical half").
"""

import math
from dataclasses import dataclass, field

TOOL_OUTPUT_CHARS = 30_000
CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class Assumptions:
    """Latency and capacity constants. Replace with calibrated values."""

    base_turn_s: float = 6.0          # a turn with an empty context: overhead + tool
    s_per_ktok_context: float = 0.03  # extra seconds per 1k tokens of live context
    decode_tok_s: float = 60.0        # output (incl. reasoning) tokens per second
    context_window_tokens: int = 200_000
    usable_context_frac: float = 0.75  # headroom for the system prompt and output
    parallel_subagents: int = 8
    compaction_s: float = 60.0         # one compaction pass
    report_tokens_per_unit: int = 250  # what a subagent hands back per unit (read)
    deliverable_tokens_per_unit: int = 80  # the merged answer's entry per unit (written)
    # Margins on both sides of the timeout.
    floor_must_exceed: float = 1.0     # even the ideal batching agent cannot finish
    careful_must_exceed: float = 1.5   # the careful agent: >= 1.5 x timeout
    delegated_must_fit: float = 0.6    # delegated estimate <= 0.6 x timeout


@dataclass(frozen=True)
class TaskShape:
    name: str
    unit_chars: list              # measured, one entry per unit: what must be READ
    judgement_turns: int          # per unit, beyond reading it (careful agent)
    orchestration_turns: int      # plan + dispatch + synthesise (delegated only)
    output_tokens_per_unit: int = 1500  # reasoning + written output per unit (assumed)
    shared_chars: int = 0         # read once per agent (docs, the brief's inputs)
    timeout_s: int = 1800
    notes: dict = field(default_factory=dict)

    @property
    def n_units(self):
        return len(self.unit_chars)


def _reads(chars):
    return max(1, math.ceil(chars / TOOL_OUTPUT_CHARS))


def _turn_s(context_tokens, a):
    return a.base_turn_s + a.s_per_ktok_context * context_tokens / 1000


def _decode_s(tokens, a):
    return tokens / a.decode_tok_s


class _Context:
    """One agent's live context: grows with what it reads, compacts at the window."""

    def __init__(self, a, start_tokens=0.0):
        self.a = a
        self.tokens = start_tokens
        self.window = a.context_window_tokens * a.usable_context_frac
        self.compactions = 0
        self.seconds = 0.0
        self.peak = start_tokens

    def turn(self, read_tokens=0.0):
        self.tokens += read_tokens
        if self.tokens > self.window:
            self.compactions += 1
            self.seconds += self.a.compaction_s
            self.tokens = self.window * 0.25  # what survives a compaction
        self.peak = max(self.peak, self.tokens)
        self.seconds += _turn_s(self.tokens, self.a)


def _careful(unit_chars, shape, a):
    ctx = _Context(a)
    for _ in range(_reads(shape.shared_chars) if shape.shared_chars else 0):
        ctx.turn(shape.shared_chars / CHARS_PER_TOKEN / _reads(shape.shared_chars))
    for chars in unit_chars:
        turns = _reads(chars) + shape.judgement_turns
        for _ in range(turns):
            ctx.turn(chars / CHARS_PER_TOKEN / turns)
        ctx.seconds += _decode_s(shape.output_tokens_per_unit, a)
    return ctx


def _floor(unit_chars, shape, a):
    ctx = _Context(a)
    total = shape.shared_chars + sum(unit_chars)
    reads = _reads(total)
    for _ in range(reads):
        ctx.turn(total / CHARS_PER_TOKEN / reads)
    per_unit = shape.output_tokens_per_unit + a.deliverable_tokens_per_unit
    ctx.seconds += _decode_s(per_unit * len(unit_chars), a)
    return ctx


def single_agent(shape, a=Assumptions()):
    return _careful(shape.unit_chars, shape, a), _floor(shape.unit_chars, shape, a)


def delegated(shape, a=Assumptions()):
    """P subagents in parallel, each careful and with a fresh context; the
    orchestrator plans, reads every report, and writes the deliverable. The
    slowest lane sets the pace."""
    p = a.parallel_subagents
    lanes = [_careful(shape.unit_chars[i::p], shape, a) for i in range(p)]
    slowest = max(l.seconds for l in lanes)
    peak = max(l.peak for l in lanes)
    report_tokens = a.report_tokens_per_unit * shape.n_units
    orchestration = (shape.orchestration_turns * _turn_s(report_tokens, a)
                     + _decode_s(a.deliverable_tokens_per_unit * shape.n_units, a))
    return slowest + orchestration, peak


def gate(shape, a=Assumptions()):
    """The by-construction half of admission. The empirical half -- real runs of
    both conditions -- is in README.md and must also pass before a task ships."""
    careful, floor = single_agent(shape, a)
    deleg_s, peak = delegated(shape, a)
    window = a.context_window_tokens * a.usable_context_frac
    t = shape.timeout_s
    checks = {
        "ideal_single_agent_times_out": floor.seconds >= a.floor_must_exceed * t,
        "careful_single_agent_times_out": careful.seconds >= a.careful_must_exceed * t,
        "delegated_fits_timeout": deleg_s <= a.delegated_must_fit * t,
        "subagent_fits_context": peak <= window,
    }
    total_tokens = int((shape.shared_chars + sum(shape.unit_chars)) / CHARS_PER_TOKEN)
    return {
        "task": shape.name,
        "units": shape.n_units,
        "total_tokens": total_tokens,
        "output_tokens": shape.output_tokens_per_unit * shape.n_units,
        "single_agent_min": round(careful.seconds / 60, 1),
        "single_agent_floor_min": round(floor.seconds / 60, 1),
        "single_agent_compactions": floor.compactions,
        "single_agent_overflows_context": total_tokens > window,
        "delegated_min": round(deleg_s / 60, 1),
        "subagent_peak_tokens": int(peak),
        "timeout_min": round(t / 60, 1),
        "checks": checks,
        "admitted": all(checks.values()),
    }
