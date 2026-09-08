"""The frozen consumer interface.

Freezing means the model, the prompt, and the version are pinned and identical
across every system under test (DESIGN.md 4). A consumer implementation must
therefore report a stable `consumer_id` -- it is part of a result's identity,
and a change to it is a benchmark version bump.
"""

from typing import Protocol

from consumer.probe import Probe, Verdict


class FrozenConsumer(Protocol):
    @property
    def consumer_id(self) -> str:
        """Stable identity: model, prompt version, settings. Goes in the result."""

    def judge(self, report: str, probes: list[Probe]) -> Verdict:
        """Answer the probes from the report alone."""


def noise_floor(consumer, report, probes, repeats=5):
    """Judge the same report repeatedly and report the spread.

    Required, not optional. Current Claude models reject `temperature` and
    `top_p` outright, so a model-backed consumer cannot be made bit-deterministic
    -- which means score differences below this floor are ties, and publishing
    the floor is the only honest way to say so (DESIGN.md 7.1).
    """
    runs = [consumer.judge(report, probes) for _ in range(repeats)]
    per_probe = []
    for i, probe in enumerate(probes):
        chosen = [r.answers[i].chosen for r in runs]
        modal = max(set(chosen), key=chosen.count)
        per_probe.append(
            {
                "question": probe.question,
                "modal_answer": modal,
                "agreement": chosen.count(modal) / len(chosen),
                "distinct_answers": len(set(chosen)),
            }
        )
    yields = [
        sum(1 for _, _, ok in r.graded(probes) if ok) / len(probes) for r in runs
    ]
    spread = max(yields) - min(yields)
    return {
        "consumer_id": consumer.consumer_id,
        "repeats": repeats,
        "decision_yield_mean": sum(yields) / len(yields),
        "decision_yield_spread": spread,
        "per_probe": per_probe,
    }
