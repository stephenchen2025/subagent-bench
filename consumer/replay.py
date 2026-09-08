"""Offline consumers: deterministic stand-ins for the model-backed one.

Every scorer in this repo is testable without an API key. That is deliberate --
the scoring pipeline is pure computation over artifacts, so its correctness
should not depend on a network call (DESIGN.md 8.2).
"""

import random

from consumer.probe import INSUFFICIENT, ProbeAnswer, Verdict


class ReplayConsumer:
    """Replays a scripted list of (choice, confidence) pairs per report.

    Used to drive the scorers over known inputs in tests.
    """

    def __init__(self, script, consumer_id="replay/v1"):
        self._script = dict(script)
        self._id = consumer_id

    @property
    def consumer_id(self):
        return self._id

    def judge(self, report, probes):
        key = report.strip()
        if key not in self._script:
            raise KeyError(f"no scripted verdict for report: {key[:60]!r}")
        answers = [ProbeAnswer(c, conf) for c, conf in self._script[key]]
        return Verdict(answers=answers, consumer_id=self._id)


class KeywordConsumer:
    """A crude programmatic consumer: picks the option best supported by the text.

    This is the program-based ablation named in DESIGN.md 9 -- perfectly
    reproducible, and much weaker than a model, which is the point of running it
    as a comparison rather than as the headline.
    """

    def __init__(self, consumer_id="keyword/v1", seed=0):
        self._id = consumer_id
        self._rng = random.Random(seed)

    @property
    def consumer_id(self):
        return self._id

    @staticmethod
    def _support(option, report):
        tokens = [t for t in option.lower().replace("::", " ").split() if len(t) > 3]
        if not tokens:
            return 0.0
        return sum(1 for t in tokens if t in report) / len(tokens)

    def judge(self, report, probes):
        text = report.lower()
        answers = []
        for probe in probes:
            scored = [
                (self._support(o, text), o)
                for o in probe.options
                if o != INSUFFICIENT
            ]
            best, choice = max(scored, default=(0.0, INSUFFICIENT))
            if best == 0.0:
                choice = INSUFFICIENT
            answers.append(ProbeAnswer(choice, min(1.0, 0.4 + 0.6 * best)))
        return Verdict(answers=answers, consumer_id=self._id)
