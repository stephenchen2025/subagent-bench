#!/usr/bin/env python3
"""Generate a task set from the family generators.

    python tools/generate_tasks.py --per-family 10 --out tasks/generated

Generated fixtures are NOT committed: the generators are the artifact, and a
held-out split is meant to be regenerated per release rather than published
(DESIGN.md 7.4). The manifest records the seeds, so any set is reproducible from
this repo alone.

Every variant passes its invariants and a behavioural probe before it is
written; a variant that fails is rejected rather than shipped.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tasks.generators import FAMILIES, generate  # noqa: E402
from tasks.generators.verify import verify  # noqa: E402


def build(per_family, out_dir, start_seed=1):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    specs_dir = out / "specs"
    specs_dir.mkdir(exist_ok=True)

    manifest, rejected = [], []
    for family in FAMILIES:
        # Draw until `per_family` DISTINCT variants land. Two seeds can pick the
        # same parameters, and identical fixtures are duplicate work dressed up
        # as coverage.
        seen, seed, accepted = set(), start_seed, 0
        while accepted < per_family and seed < start_seed + per_family * 20:
            variant = generate(family, seed, ROOT / "envs/py_svc/repo", out)
            seed += 1
            signature = json.dumps(variant.params, sort_keys=True)
            if signature in seen:
                shutil.rmtree(variant.fixture, ignore_errors=True)
                continue
            seen.add(signature)
            try:
                verify(variant)
            except AssertionError as exc:
                rejected.append((variant.task_id, str(exc)[:120]))
                continue
            accepted += 1
            (specs_dir / f"{variant.task_id}.json").write_text(
                json.dumps(variant.spec, indent=2) + "\n"
            )
            manifest.append(
                {"task_id": variant.task_id, "family": family,
                 "seed": variant.seed, "params": variant.params}
            )

    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest, rejected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-family", type=int, default=10)
    parser.add_argument("--out", default=str(ROOT / "tasks" / "generated"))
    parser.add_argument("--start-seed", type=int, default=1)
    args = parser.parse_args()

    manifest, rejected = build(args.per_family, args.out, args.start_seed)
    by_family = {}
    for entry in manifest:
        by_family[entry["family"]] = by_family.get(entry["family"], 0) + 1
    for family, count in sorted(by_family.items()):
        print(f"  {family:24} {count}")
    print(f"\n{len(manifest)} task(s) written to {args.out}")
    if rejected:
        print(f"\n{len(rejected)} rejected by the behavioural gate:")
        for task_id, reason in rejected:
            print(f"  {task_id}: {reason}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
