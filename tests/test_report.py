"""The report must not let a headline travel without its cost (DESIGN.md 5.7)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from report.render import frontier_table, markdown  # noqa: E402


def _card(**overrides):
    card = {
        "n_episodes": 3,
        "decision_yield": 0.5, "honest_abstention": 1.0, "false_certainty": 0.0,
        "cir_yield": 0.5, "critical_omission_rate": 0.25,
        "unsupported_claim_rate": 0.0,
        "calibration": {"auroc": None, "ece": 0.2, "overconfidence": None},
        "scope": {"clean_rate": 1.0, "over_reach_episodes": 0, "hard_fails": {}},
        "cost": {"mean_tokens": 3400, "mean_cost_ratio": 1.1,
                 "over_budget_episodes": 0},
        "dy_at_budget": {"DY@2000": 0.0},
        "frontier": [{"budget_tokens": 2000, "dy_at_budget": 0.0,
                      "mean_tokens_spent": 6000, "n": 3, "over_budget": 3}],
        "by_family": {"F2_poisoned_premise": {"n": 3, "decision_yield": 0.5,
                                              "scope_clean_rate": 1.0}},
    }
    card.update(overrides)
    return card


def test_cost_is_rendered_before_the_axes():
    body = markdown(_card())
    assert body.index("## Yield vs cost") < body.index("## Axes")


def test_undefined_statistics_render_as_na_not_zero():
    """AUROC is undefined with one class; printing 0.000 would be a lie."""
    body = markdown(_card())
    assert "| calibration AUROC | n/a |" in body


def test_hard_fails_are_counted_not_averaged():
    body = markdown(_card(scope={"clean_rate": 0.5, "over_reach_episodes": 1,
                                 "hard_fails": {"git_push": 2}}))
    assert "| `git_push` | 2 |" in body
    assert "never averaged" in body


def test_no_hard_fails_still_says_so():
    assert "None. (Counted" in markdown(_card())


def test_ungraded_episodes_are_named():
    body = markdown(_card(ungraded_for_fabrication=["a", "b"]))
    assert "Not gradeable for fabrication" in body
    assert "`a`" in body and "`b`" in body


def test_long_ungraded_list_is_truncated_with_a_count():
    body = markdown(_card(ungraded_for_fabrication=[f"t{i}" for i in range(25)]))
    assert "and 5 more" in body


def test_over_budget_episodes_are_called_out():
    assert "exceeded their token cap" in markdown(
        _card(cost={"mean_tokens": 1, "mean_cost_ratio": None,
                    "over_budget_episodes": 4})
    )


def test_caveat_note_travels_with_the_report():
    assert "> not a measurement" in markdown(_card(), note="not a measurement")


def test_frontier_table_handles_no_budgeted_runs():
    assert "No budgeted runs" in frontier_table({"frontier": []})
