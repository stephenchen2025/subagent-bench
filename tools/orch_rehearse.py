#!/usr/bin/env python3
"""Rehearse the orchestrator track with scripted policies. No model, no key.

Runs every rehearsal system (orch/policies.py) over the generated task set
through the real reference harness, grades with the real verifier, and renders
the report. The question it answers is whether the metrics separate policies the
way they are supposed to:

- solo is flat, and falls off on W and P as size grows;
- judicious delegation captures the ceiling on W and P and pays no tax on C and S;
- eager delegation captures W and P but pays a tax on C and a cost ratio on S;
- sloppy delegation shows up as low coverage, duplication and synthesis loss.

Every agent is a perfect reader, so solo-xl matches delegate: with no context rot,
more tokens are as good as more agents. Whether that holds for a real model is
the live run's question, and the report says so.

    python tools/orch_rehearse.py --seeds 1 2 3
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch import policies  # noqa: E402
from orch.emit import generate_set  # noqa: E402
from orch.local import run_local  # noqa: E402
from orch.report import render  # noqa: E402

SYSTEMS = ["solo", "solo-xl", "oracle-split", "judicious", "eager", "sloppy"]

PREAMBLE = """\
**A rehearsal, not a measurement.** Every agent here is a scripted *perfect reader*:
it knows the right answer for any ticket or service it has actually read. Reading
skill is held perfect so that differences come only from structure: who hits a
wall, how work is partitioned, and what survives synthesis. That is what the
metrics claim to measure, and this checks that they separate policies the way they
should. It says nothing about any real model.

Expect solo-xl to match delegate here. A perfect reader suffers no context rot, so
more tokens are as good as more agents. The live run exists to test whether that
holds for a real model.
"""


def condition_for(system):
    mode, _ = policies.LEADS[system]
    return f"delegate:{system}" if mode == "delegate" else mode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    parser.add_argument("--systems", nargs="+", default=SYSTEMS)
    parser.add_argument("--out", default=str(ROOT / "build" / "orch-rehearsal"))
    args = parser.parse_args(argv)

    out = Path(args.out)
    tasks = generate_set(seeds=tuple(args.seeds))
    records, t0 = [], time.time()
    for task in tasks:
        for system in args.systems:
            mode, lead, worker_factory = policies.build(system, task)
            record = run_local(
                task, mode, lead, worker_factory, out_dir=out / "runs" / f"{task.id}__{system}",
                system="rehearsal", condition=condition_for(system),
            )
            records.append(record)
    (out / "records.json").write_text(json.dumps(records, indent=2))
    report = render(records, out, title="Orchestrator track: rehearsal", preamble=PREAMBLE)
    print(f"{len(records)} runs in {time.time() - t0:.0f}s -> {report}")
    return records


if __name__ == "__main__":
    main()
