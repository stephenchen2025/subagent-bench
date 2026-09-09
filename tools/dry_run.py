#!/usr/bin/env python3
"""Exercise the whole pipeline at Milestone-1 scale, with no model.

    python tools/dry_run.py [--per-family 10]

This is a PLUMBING REHEARSAL, not a measurement. Three synthetic "systems" of
known quality are run over the generated task set and scored by a consumer that
is told which system it is reading. Nothing here says anything about any real
model; what it checks is that generation, scoring, aggregation, the frontier and
the report all compose at 30 tasks instead of 3.

The systems are chosen to exercise specific machinery:
  thorough    -- the spec's own oracle report; should score at the ceiling
  terse       -- uninformative but honest; should abstain, not mislead
  fabricating -- cites evidence the trajectory does not contain
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer.probe import INSUFFICIENT, Probe, ProbeAnswer, Verdict  # noqa: E402
from report.render import markdown  # noqa: E402
from scorers.aggregate import score_episode, scorecard  # noqa: E402
from scorers.episode import Episode, Usage  # noqa: E402
from tools.generate_tasks import build  # noqa: E402

BUDGETS = (2000, 10000, 50000)
# Absolute spend: thorough work costs what it costs, which is the whole point of
# reporting yield at a budget rather than in the abstract.
SPEND = {"thorough": 6000, "terse": 1200, "fabricating": 1500}
FAKE_EVIDENCE = "src/legacy/shim.py:404"


class TierConsumer:
    """A consumer told which system wrote the report. Simulation, not judgement."""

    consumer_id = "dry-run/tier-oracle"

    def __init__(self, tier):
        self.tier = tier

    def judge(self, report, probes):
        answers = []
        for probe in probes:
            if self.tier == "thorough":
                answers.append(ProbeAnswer(probe.answer, 0.92))
            elif self.tier == "terse":
                answers.append(ProbeAnswer(INSUFFICIENT, 0.45))
            else:
                wrong = next(
                    (o for o in probe.options
                     if o not in (probe.answer, INSUFFICIENT)),
                    INSUFFICIENT,
                )
                answers.append(ProbeAnswer(wrong, 0.88))
        return Verdict(answers=answers, consumer_id=f"dry-run/{self.tier}")


def synth_trajectory(spec):
    """A plausible record of what a diligent subagent would have observed."""
    invariants = spec["ground_truth"].get("invariants", {})
    steps = [{"command": "find tests -name '*.py'",
              "output": "tests/test_dedup.py\ntests/test_parse.py\ntests/test_report.py"}]
    for rel in invariants.get("absent", []):
        steps.append({"command": f"ls {rel}",
                      "output": f"ls: cannot access '{rel}': No such file or directory"})
    for rel, needle in invariants.get("contains", []):
        steps.append({"command": f"cat {rel}", "output": f"{rel}\n{needle}"})
    for rel, needle in invariants.get("not_contains", []):
        steps.append({"command": f"grep -n '{needle}' {rel}", "output": ""})
    for symbol, _own in invariants.get("no_importers", []):
        steps.append({"command": f"grep -rn {symbol} src/ tests/",
                      "output": f"src/: only its own definition"})
    return steps


def synth_report(spec, tier):
    if tier == "thorough":
        return spec["oracle_report"]
    if tier == "terse":
        return "I looked into it. It behaves as described and explains what you're seeing."
    return (
        f"The cause is at {FAKE_EVIDENCE}, where a legacy shim overrides the "
        "configured behaviour. Removing it resolves the issue."
    )


def episodes_for(spec, tier):
    trajectory = synth_trajectory(spec)
    report = synth_report(spec, tier)
    for budget in BUDGETS:
        spend = SPEND[tier]
        yield Episode(
            task_id=spec["id"], family=spec["family"], report=report,
            trajectory=trajectory,
            effects={"touched": [], "over_reach": [], "under_reach": [],
                     "hard_fails": [], "clean": True},
            usage=Usage(input_tokens=spend, tool_calls=len(trajectory)),
            budget_tokens=budget,
            reference_tokens=spec["budget"].get("reference_tokens", 0),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=10)
    parser.add_argument("--out", default=str(ROOT / "build" / "dry_run"))
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest, rejected = build(args.per_family, ROOT / "tasks" / "generated")
    if rejected:
        print(f"{len(rejected)} variant(s) rejected by the behavioural gate")
    specs = [
        json.loads((ROOT / "tasks/generated/specs" / f"{m['task_id']}.json").read_text())
        for m in manifest
    ]
    print(f"{len(specs)} tasks; {len(SPEND)} systems x {len(BUDGETS)} budgets = "
          f"{len(specs) * len(SPEND) * len(BUDGETS)} episodes\n")

    note = ("PLUMBING REHEARSAL. The consumer is told which system wrote each "
            "report, so these numbers describe the pipeline, not any model.")
    summary = {}
    for tier in SPEND:
        consumer = TierConsumer(tier)
        rows = [
            score_episode(episode, spec, consumer)
            for spec in specs
            for episode in episodes_for(spec, tier)
        ]
        card = scorecard(rows, budgets=BUDGETS)
        summary[tier] = card
        (out / f"{tier}.md").write_text(
            markdown(card, title=f"HANDOFF dry run — {tier}", note=note)
        )
        dy = card["dy_at_budget"]
        print(f"{tier:12} yield {card['decision_yield']:.2f}  "
              f"false-cert {card['false_certainty']:.2f}  "
              f"unsupported {card['unsupported_claim_rate']:.2f}  "
              f"AUROC {card['calibration']['auroc'] if card['calibration']['auroc'] is None else format(card['calibration']['auroc'], '.2f')}  "
              + "  ".join(f"{k} {v:.2f}" for k, v in dy.items()))

    (out / "scorecards.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"\nreports written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
