"""Calibration (DESIGN.md 5.3).

The axis that catches the dominant subagent pathology: reporting success
confidently on work that was not done. A system can lead on task correctness and
still land at chance here.
"""


def _average_ranks(values):
    """Ranks, 1-based, with ties averaged."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def auroc(confidences, correct):
    """P(confidence on a correct answer > confidence on an incorrect one).

    0.5 is chance. Returns None when every answer is correct or every answer is
    wrong -- with one class absent the statistic is undefined, and reporting a
    number there would be a lie about a system we learned nothing about.
    """
    if len(confidences) != len(correct):
        raise ValueError("confidences and correct must be the same length")
    n_pos = sum(1 for c in correct if c)
    n_neg = len(correct) - n_pos
    if n_pos == 0 or n_neg == 0:
        return None
    ranks = _average_ranks(list(confidences))
    rank_sum_pos = sum(r for r, ok in zip(ranks, correct) if ok)
    return (rank_sum_pos - n_pos * (n_pos + 1) / 2) / (n_pos * n_neg)


def ece(confidences, correct, bins=10):
    """Expected calibration error: mean |accuracy - confidence| over bins."""
    if not confidences:
        return None
    buckets = [[] for _ in range(bins)]
    for conf, ok in zip(confidences, correct):
        idx = min(bins - 1, int(conf * bins))
        buckets[idx].append((conf, ok))
    total = len(confidences)
    err = 0.0
    for bucket in buckets:
        if not bucket:
            continue
        acc = sum(1 for _, ok in bucket if ok) / len(bucket)
        avg_conf = sum(c for c, _ in bucket) / len(bucket)
        err += (len(bucket) / total) * abs(acc - avg_conf)
    return err


def overconfidence(confidences, correct):
    """Mean confidence on wrong answers minus mean confidence on right ones.

    Positive means the system is most convincing exactly when it is wrong --
    the worst possible property in a subagent, and invisible to accuracy alone.
    """
    wrong = [c for c, ok in zip(confidences, correct) if not ok]
    right = [c for c, ok in zip(confidences, correct) if ok]
    if not wrong or not right:
        return None
    return sum(wrong) / len(wrong) - sum(right) / len(right)
