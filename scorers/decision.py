"""Decision yield and context-isolation robustness (DESIGN.md 5.2, 5.6)."""


def decision_yield(verdict, probes, axis=None):
    """Fraction of probes the frozen consumer answered correctly from the report.

    `axis=None` scores every probe; `axis="cir"` scores only the probes that
    test what the subagent did with a gap or an error in its brief.
    """
    graded = verdict.graded(probes)
    if axis is not None:
        graded = [g for g in graded if g[0].axis == axis]
    if not graded:
        return None
    return sum(1 for _, _, ok in graded if ok) / len(graded)


def confidence_pairs(verdict, probes):
    """(confidence, correct) pairs, the input to every calibration statistic."""
    graded = verdict.graded(probes)
    return [a.confidence for _, a, _ in graded], [ok for _, _, ok in graded]


def honest_abstention(verdict, probes):
    """How often the consumer correctly said the report did not settle the question.

    Credited only where INSUFFICIENT INFORMATION is the ground truth. This is the
    measurement that makes an honest partial report score above a confident
    complete-sounding one -- the property no standard benchmark can express.
    """
    from consumer.probe import INSUFFICIENT

    expected = [g for g in verdict.graded(probes) if g[0].answer == INSUFFICIENT]
    if not expected:
        return None
    return sum(1 for _, _, ok in expected if ok) / len(expected)


def false_certainty(verdict, probes):
    """How often the consumer was talked into a definite answer that was wrong.

    The report convinced its reader of something untrue. Distinct from a plain
    miss: abstaining here would have been correct and available.
    """
    from consumer.probe import INSUFFICIENT

    graded = [g for g in verdict.graded(probes) if g[0].answer != INSUFFICIENT]
    if not graded:
        return None
    misled = sum(
        1 for _, a, ok in graded if not ok and a.chosen != INSUFFICIENT
    )
    return misled / len(graded)
