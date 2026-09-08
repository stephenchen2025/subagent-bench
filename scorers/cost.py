"""Cost proportionality and the headline (DESIGN.md 5.5, 5.7).

Budgets are denominated in tokens, never currency. A dollar budget buys a cheap
model more work than an expensive one at nominally equal budget, which would mix
model price into a metric about delegation skill.
"""


def cost_ratio(episode):
    """Tokens spent relative to the oracle-condition reference for the task."""
    if not episode.reference_tokens:
        return None
    return episode.usage.total_tokens / episode.reference_tokens


def early_return_credit(episode, decision_yield_value):
    """Credit for stopping early with a useful report instead of thrashing.

    Only meaningful where the task is genuinely blocked or over-budget (F6): the
    correct move is a well-formed partial at a fraction of the budget. Returning
    early with nothing useful earns nothing -- the yield term sees to that.
    """
    if not episode.returned_early or not episode.budget_tokens:
        return None
    spent = episode.usage.total_tokens / episode.budget_tokens
    return max(0.0, decision_yield_value * (1.0 - spent))


def decision_yield_at_budget(rows, budget):
    """DY@B: mean decision yield among episodes run under budget B.

    An episode that overran its cap scores zero: it was cut off, and whatever it
    would have reported never reached the orchestrator.
    """
    runs = [r for r in rows if r.get("budget_tokens") == budget]
    if not runs:
        return None
    total = 0.0
    for row in runs:
        if row.get("over_budget"):
            continue
        total += row.get("decision_yield") or 0.0
    return total / len(runs)


def frontier(rows):
    """The yield-vs-cost curve. Required alongside any headline number."""
    budgets = sorted({r["budget_tokens"] for r in rows if r.get("budget_tokens")})
    points = []
    for budget in budgets:
        runs = [r for r in rows if r["budget_tokens"] == budget]
        spent = [r["usage_tokens"] for r in runs]
        points.append(
            {
                "budget_tokens": budget,
                "dy_at_budget": decision_yield_at_budget(rows, budget),
                "mean_tokens_spent": sum(spent) / len(spent) if spent else 0.0,
                "n": len(runs),
                "over_budget": sum(1 for r in runs if r.get("over_budget")),
            }
        )
    return points
