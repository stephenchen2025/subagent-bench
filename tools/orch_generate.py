#!/usr/bin/env python3
"""Generate the orchestrator-track task set as Harbor task directories.

    python tools/orch_generate.py                         # every family, default sizes, seeds 1-3
    python tools/orch_generate.py --seeds 1 --families W P
    python tools/orch_generate.py --sizes W=6,24,72,144   # bigger N for a 200k-window scaffold

Then validate every task with Harbor's oracle agent (each must score 1.0):

    harbor run -p build/orch/tasks -a oracle -n 4
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch.emit import emit_set, generate_set  # noqa: E402


def parse_sizes(values):
    sizes = {}
    for value in values or []:
        family, _, numbers = value.partition("=")
        sizes[family.upper()] = tuple(int(n) for n in numbers.split(",") if n)
    return sizes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--families", nargs="+", default=None)
    parser.add_argument("--sizes", nargs="+", default=None, help="FAMILY=n,n,...")
    parser.add_argument("--out", default=str(ROOT / "build" / "orch" / "tasks"))
    args = parser.parse_args(argv)
    tasks = generate_set(sizes=parse_sizes(args.sizes), seeds=tuple(args.seeds),
                         families=[f.upper() for f in args.families] if args.families else None)
    emit_set(tasks, args.out)
    by_label = Counter(t.label for t in tasks)
    print(f"{len(tasks)} tasks -> {args.out} ({dict(by_label)})")
    return tasks


if __name__ == "__main__":
    main()
