#!/usr/bin/env python3
"""Run the orchestrator track for real: models x conditions x tasks, no Docker.

    python tools/orch_run.py --models anthropic/claude-sonnet-5 --seeds 1 --max-cost 25

Uses mini-swe-agent's LocalEnvironment on a temp copy of each task (the same
path the rehearsal takes), so ANTHROPIC_API_KEY is the only prerequisite. That
is a first-run convenience, not a sandbox: a live model runs real commands on
this machine. For anything beyond a first look, run the same tasks under Harbor:

    harbor run -p datasets/orch-v0.1 -a orch.harbor_agent:OrchMiniAgent \\
        -m anthropic/claude-sonnet-5 --ak mode=delegate

Every completed run is written to disk as it finishes, so an interrupted run
costs nothing to restart. The cost cap is checked before each run, from the
dollar totals mini reports, and can overshoot by at most one run.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch.emit import generate_set  # noqa: E402
from orch.harness import MODES  # noqa: E402
from orch.report import render  # noqa: E402

DEFAULT_CONDITIONS = ["solo", "delegate", "oracle-split", "solo-xl"]


def _spent(records):
    total = 0.0
    for r in records:
        tel = r["telemetry"]
        total += tel["lead"].get("cost_usd", 0.0) + sum(w.get("cost_usd", 0.0) for w in tel["workers"])
    return total


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--worker-model", default=None, help="defaults to each lead's model")
    parser.add_argument("--conditions", nargs="+", default=DEFAULT_CONDITIONS, choices=MODES)
    parser.add_argument("--seeds", type=int, nargs="+", default=[1])
    parser.add_argument("--families", nargs="+", default=None)
    parser.add_argument("--max-cost", type=float, default=25.0, help="USD, across all models")
    parser.add_argument("--latency", default="2", help="svcctl latency in seconds (P family)")
    parser.add_argument("--out", default=str(ROOT / "build" / "orch-live"))
    args = parser.parse_args(argv)

    from minisweagent.models import get_model

    out = Path(args.out)
    tasks = generate_set(seeds=tuple(args.seeds),
                         families=[f.upper() for f in args.families] if args.families else None)
    records = [json.loads(p.read_text()) for p in sorted(out.glob("runs/*/record.json"))]
    done = {(r["system"], r["condition"], r["task_id"]) for r in records}
    from orch.local import run_local

    for model in args.models:
        for task in tasks:
            for condition in args.conditions:
                if (model, condition, task.id) in done:
                    continue
                if _spent(records) >= args.max_cost:
                    print(f"cost cap ${args.max_cost:.2f} reached; rerun to resume")
                    return _finish(records, out)
                worker = args.worker_model or model
                run_dir = out / "runs" / f"{model.replace('/', '_')}__{condition}__{task.id}"
                record = run_local(task, condition, get_model(model), lambda: get_model(worker),
                                   out_dir=run_dir, latency=args.latency, timeout=120,
                                   system=model, condition=condition)
                records.append(record)
                print(f"{model} {condition:12} {task.id:18} reward={record['reward']['reward']:.2f} "
                      f"subagents={len(record['telemetry']['workers'])} "
                      f"spent=${_spent(records):.2f}")
    return _finish(records, out)


def _finish(records, out):
    (out / "records.json").write_text(json.dumps(records, indent=2))
    report = render(records, out, title="Orchestrator track: live run")
    print(f"{len(records)} runs -> {report}")
    return records


if __name__ == "__main__":
    main()
