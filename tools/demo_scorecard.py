#!/usr/bin/env python3
"""Score two subagents that did identical work but wrote different reports.

Run: python tools/demo_scorecard.py

No API key and no network: the consumer is a scripted stand-in. The point is to
show what the six axes see when task correctness and scope discipline are held
constant and only the report varies -- which is the whole claim HANDOFF makes.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from consumer.replay import KeywordConsumer
from scorers.aggregate import render, score_episode, scorecard
from tests.test_pipeline import CONSUMER, PRECISE, SPEC, TERSE, _episode


def main():
    rows = []
    for label, report in [("precise", PRECISE), ("terse", TERSE)]:
        row = score_episode(_episode(report), SPEC, CONSUMER)
        rows.append(row)
        print(f"--- {label} subagent " + "-" * (52 - len(label)))
        print(f"  report              {report[:60]}...")
        print(f"  decision yield      {row['decision_yield']:.2f}")
        print(f"  CIR yield           {row['cir_yield']:.2f}")
        print(f"  false certainty     {row['false_certainty']:.2f}")
        print(f"  omission rate       {row['critical_omission_rate']:.2f}")
        print(f"  unsupported claims  {row['unsupported_claim_rate']:.2f}")
        print(f"  scope clean         {row['scope']['clean']}")
        print(f"  tokens              {row['usage_tokens']}")
        print()

    print("=== scorecard " + "=" * 45)
    print(render(scorecard(rows, budgets=(SPEC['budget']['max_tokens'],))))

    print()
    print("=== program-based consumer ablation (DESIGN.md 9, Q1) " + "=" * 6)
    kw = KeywordConsumer()
    for label, report in [("precise", PRECISE), ("terse", TERSE)]:
        row = score_episode(_episode(report), SPEC, kw)
        print(f"  {label:<8} decision yield {row['decision_yield']:.2f}")
    print("  It scores the precise report at zero. On the first probe it picks")
    print("  settings/upload.yml -- a file the report names precisely in order to")
    print("  RULE IT OUT. A keyword consumer cannot tell a mention from an")
    print("  assertion, and it abstains on every yes/no probe. It does not merely")
    print("  compress the gap it is meant to measure; it inverts it.")
    print("  That is the argument for a model-backed frozen consumer (DESIGN.md 9).")


if __name__ == "__main__":
    main()
