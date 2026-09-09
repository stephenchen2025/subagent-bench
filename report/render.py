"""Turn a scorecard into a report.

DESIGN.md 5.7 requires the yield-vs-cost frontier alongside any headline: a
quality number without its cost is not a HANDOFF result. So the frontier is
rendered first and the headline never appears alone.

Two things are deliberately never averaged away: hard fails are a count, and
episodes with no trajectory are named, because they were not gradeable for
fabrication and a reader has to know which.
"""


def _fmt(value, spec=".3f", missing="n/a"):
    return missing if value is None else format(value, spec)


def _bar(value, width=28):
    """A text bar for the frontier. The published plot is a chart; this is for
    a terminal, and it should not pretend to be more precise than it is."""
    if value is None:
        return " " * width
    filled = int(round(max(0.0, min(1.0, value)) * width))
    return "█" * filled + "·" * (width - filled)


def frontier_table(card):
    rows = card.get("frontier") or []
    if not rows:
        return "_No budgeted runs._\n"
    out = [
        "| budget (tokens) | DY@B | mean spent | n | over budget |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        out.append(
            f"| {row['budget_tokens']:,} | {_fmt(row['dy_at_budget'])} | "
            f"{row['mean_tokens_spent']:,.0f} | {row['n']} | {row['over_budget']} |"
        )
    out.append("")
    out.append("```")
    for row in rows:
        out.append(
            f"{row['budget_tokens']:>7,}  {_bar(row['dy_at_budget'])}  "
            f"{_fmt(row['dy_at_budget'])}"
        )
    out.append("```")
    return "\n".join(out) + "\n"


def markdown(card, title="HANDOFF run", note=None):
    """Render a full report. `note` is for caveats that must travel with it."""
    cal = card["calibration"]
    scope = card["scope"]
    cost = card["cost"]
    lines = [f"# {title}", ""]
    if note:
        lines += [f"> {note}", ""]

    lines += ["## Yield vs cost", "",
              "A quality number without its cost is not a result (DESIGN.md 5.7).",
              "", frontier_table(card), ""]

    lines += ["## Axes", "", "| axis | value |", "|---|---|",
              f"| episodes | {card['n_episodes']} |",
              f"| decision yield | {_fmt(card['decision_yield'])} |",
              f"| honest abstention | {_fmt(card['honest_abstention'])} |",
              f"| false certainty | {_fmt(card['false_certainty'])} |",
              f"| context-isolation (CIR) yield | {_fmt(card['cir_yield'])} |",
              f"| critical omission rate | {_fmt(card['critical_omission_rate'])} |",
              f"| unsupported claim rate | {_fmt(card['unsupported_claim_rate'])} |",
              f"| calibration AUROC | {_fmt(cal['auroc'])} |",
              f"| calibration ECE | {_fmt(cal['ece'])} |",
              f"| overconfidence gap | {_fmt(cal['overconfidence'])} |",
              f"| scope clean rate | {_fmt(scope['clean_rate'])} |",
              f"| mean tokens | {_fmt(cost['mean_tokens'], ',.0f')} |",
              f"| mean cost ratio vs oracle | {_fmt(cost['mean_cost_ratio'])} |", ""]

    lines += ["## Hard fails", ""]
    if scope["hard_fails"]:
        lines += ["| action | episodes |", "|---|---|"]
        lines += [f"| `{name}` | {count} |" for name, count in scope["hard_fails"].items()]
        lines += ["", "Hard fails are counted, never averaged into a score.", ""]
    else:
        lines += ["None. (Counted, never averaged into a score.)", ""]

    lines += ["## By family", "", "| family | n | decision yield | scope clean |",
              "|---|---|---|---|"]
    for family, row in card["by_family"].items():
        lines.append(
            f"| {family} | {row['n']} | {_fmt(row['decision_yield'])} | "
            f"{_fmt(row['scope_clean_rate'])} |"
        )
    lines.append("")

    ungraded = card.get("ungraded_for_fabrication")
    if ungraded:
        lines += ["## Not gradeable for fabrication", "",
                  "These episodes carried no trajectory, so unsupported-claim and "
                  "calibration scoring did not apply to them:", ""]
        lines += [f"- `{task_id}`" for task_id in ungraded[:20]]
        if len(ungraded) > 20:
            lines.append(f"- …and {len(ungraded) - 20} more")
        lines.append("")

    over = cost["over_budget_episodes"]
    if over:
        lines += [f"_{over} episode(s) exceeded their token cap and scored zero "
                  "yield at that budget._", ""]
    return "\n".join(lines)
