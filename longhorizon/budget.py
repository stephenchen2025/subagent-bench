"""Why a single agent times out on these tasks and a delegating one does not.

A long-horizon task here is N independent *units* (a service to audit, a package
to migrate, a host's logs to read) plus a synthesis step. Each unit costs:

    reads     = ceil(unit_chars / TOOL_OUTPUT_CHARS)   tool calls just to see it
    judgement = task-specific turns to reason, edit, test, and write it up

and every turn costs wall-clock time. Three limits bind:

1. **Wall clock** (`task.toml` [agent].timeout_sec) -- the one Harbor enforces.
2. **Context** -- one agent reading all N units holds N * unit_tokens. Past the
   window it must compact, and compaction discards exactly the per-unit detail
   the deliverable needs.
3. **Turn latency grows with context** -- a single agent's later turns are
   slower than a fresh subagent's, because every turn re-reads a longer prefix.

A single agent pays for every unit's turns in sequence, at an ever-longer
context. An orchestrator with P parallel subagents pays ceil(N/P) units' worth
of turns, each at a short context, plus its own planning and synthesis turns.

Nothing here is measured yet. The latency constants are assumptions to be
replaced by a calibration run (see longhorizon/README.md, "Admission gate");
the unit sizes are NOT assumptions -- `measure()` reads them off a generated
workspace, so the model is only as wrong as its latency constants.
"""

import math
from dataclasses import dataclass, field

TOOL_OUTPUT_CHARS = 30_000
CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class Assumptions:
    """Latency and capacity constants. Replace with calibrated values."""

    base_turn_s: float = 6.0          # a turn with an empty context: decode + tool
    s_per_ktok_context: float = 0.03  # extra seconds per 1k tokens of live context
    context_window_tokens: int = 200_000
    usable_context_frac: float = 0.75  # headroom for the system prompt and output
    parallel_subagents: int = 8
    compaction_s: float = 60.0         # one compaction pass
    # A task is admitted only with margin on both sides of the timeout.
    single_must_exceed: float = 1.5    # single-agent estimate >= 1.5 x timeout
    delegated_must_fit: float = 0.6    # delegated estimate <= 0.6 x timeout


@dataclass(frozen=True)
class TaskShape:
    name: str
    unit_chars: list            # measured, one entry per unit
    judgement_turns: int        # per unit, beyond reading it
    orchestration_turns: int    # plan + dispatch + synthesise (delegated only)
    shared_chars: int = 0       # read once per agent (docs, the brief's inputs)
    timeout_s: int = 1800
    notes: dict = field(default_factory=dict)

    @property
    def n_units(self):
        return len(self.unit_chars)


def _reads(chars):
    return max(1, math.ceil(chars / TOOL_OUTPUT_CHARS))


def _turn_s(context_tokens, a):
    return a.base_turn_s + a.s_per_ktok_context * context_tokens / 1000


def single_agent_seconds(shape, a=Assumptions()):
    """One agent, every unit in sequence, context growing as it reads."""
    window = a.context_window_tokens * a.usable_context_frac
    context = shape.shared_chars / CHARS_PER_TOKEN
    seconds = _reads(shape.shared_chars) * _turn_s(context, a) if shape.shared_chars else 0.0
    compactions = 0
    for chars in shape.unit_chars:
        unit_tokens = chars / CHARS_PER_TOKEN
        turns = _reads(chars) + shape.judgement_turns
        for _ in range(turns):
            context += unit_tokens / turns
            if context > window:
                compactions += 1
                seconds += a.compaction_s
                context = window * 0.25  # what survives a compaction
            seconds += _turn_s(context, a)
    return seconds, compactions


def delegated_seconds(shape, a=Assumptions()):
    """P subagents in parallel, each with a fresh context; the orchestrator plans
    and synthesises. The slowest subagent sets the pace."""
    p = a.parallel_subagents
    lanes = [shape.unit_chars[i::p] for i in range(p)]
    slowest = 0.0
    peak_context = 0.0
    for lane in lanes:
        context = shape.shared_chars / CHARS_PER_TOKEN
        seconds = _reads(shape.shared_chars) * _turn_s(context, a) if shape.shared_chars else 0.0
        for chars in lane:
            unit_tokens = chars / CHARS_PER_TOKEN
            turns = _reads(chars) + shape.judgement_turns
            for _ in range(turns):
                context += unit_tokens / turns
                seconds += _turn_s(context, a)
        slowest = max(slowest, seconds)
        peak_context = max(peak_context, context)
    # The orchestrator reads only reports, so its context stays small.
    orchestration = shape.orchestration_turns * _turn_s(20_000, a)
    return slowest + orchestration, peak_context


def gate(shape, a=Assumptions()):
    """The by-construction half of admission. The empirical half -- real runs of
    both conditions -- is in README.md and must also pass before a task ships."""
    single_s, compactions = single_agent_seconds(shape, a)
    deleg_s, peak = delegated_seconds(shape, a)
    window = a.context_window_tokens * a.usable_context_frac
    checks = {
        "single_agent_times_out": single_s >= a.single_must_exceed * shape.timeout_s,
        "delegated_fits_timeout": deleg_s <= a.delegated_must_fit * shape.timeout_s,
        "subagent_fits_context": peak <= window,
    }
    return {
        "task": shape.name,
        "units": shape.n_units,
        "total_tokens": int((shape.shared_chars + sum(shape.unit_chars)) / CHARS_PER_TOKEN),
        "single_agent_min": round(single_s / 60, 1),
        "single_agent_compactions": compactions,
        # Informative, not required: an agent that navigates well reads only the
        # essential part of each unit, so overflow is likely but not guaranteed.
        # Wall-clock turns are the limit that binds regardless.
        "single_agent_overflows_context":
            (shape.shared_chars + sum(shape.unit_chars)) / CHARS_PER_TOKEN > window,
        "delegated_min": round(deleg_s / 60, 1),
        "subagent_peak_tokens": int(peak),
        "timeout_min": round(shape.timeout_s / 60, 1),
        "checks": checks,
        "admitted": all(checks.values()),
    }
