#!/usr/bin/env python3
"""Summarise a `harbor run -a oracle` job over the task set as markdown.

Every task's oracle solution must score 1.0; a task that doesn't is broken and
must not ship (ORCHESTRATOR.md 3). This turns the job directory into a small,
committable record of that check.

    python tools/orch_oracle_summary.py jobs/<oracle-job> > results/harbor-oracle.md
"""

import json
import sys
from pathlib import Path


def main(job):
    rows = []
    for reward in sorted(Path(job).rglob("verifier/reward.json")):
        trial = reward.parent.parent
        task = trial.name.split("__")[0]
        result = json.loads((trial / "result.json").read_text())
        rows.append((task, json.loads(reward.read_text())["reward"],
                     result.get("started_at", ""), result.get("exception_info")))
    ok = sum(1 for _, r, _, e in rows if r == 1.0 and not e)
    print("# Harbor oracle validation\n")
    print(f"`harbor run -a oracle` over `datasets/orch-v0.2`: **{ok}/{len(rows)} tasks score 1.0.**\n")
    print("Each task's Docker image was built, its `solution/solve.sh` run, and its "
          "verifier scored the result.\n")
    print("| task | reward | exception |\n|---|---|---|")
    for task, r, _, e in rows:
        print(f"| {task} | {r} | {'yes' if e else '–'} |")
    return 0 if ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
