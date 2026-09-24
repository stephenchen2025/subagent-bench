#!/usr/bin/env python3
"""Turn Harbor job directories into orchestrator-track records and a report.

    python tools/orch_collect.py jobs/2026-09-24__solo jobs/2026-09-24__delegate
    python tools/orch_collect.py jobs/cc-solo=claude-code:solo jobs/cc-agent=claude-code:delegate

Each trial contributes one record: the verifier's reward.json and answer.json,
plus telemetry. Reference-harness trials carry telemetry.json; any other agent
(Claude Code, Codex CLI, ...) is reconstructed from Harbor's ATIF
trajectory.json (orch/atif.py). Ground truth is regenerated from the task id --
generators are deterministic, so no task directory is needed.

System and condition are detected from the job config (the reference harness's
`mode` kwarg; Claude Code with `disallowed_tools` containing Agent is solo) and
can be forced with JOBDIR=system:condition.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orch.atif import telemetry_from_atif  # noqa: E402
from orch.families import FAMILIES  # noqa: E402
from orch.report import render  # noqa: E402

TASK_ID = re.compile(r"orch-([a-z])-n(\d+)-s(\d+)")


def _load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None


def detect(config):
    agent = config.get("agent") or {}
    kwargs = agent.get("kwargs") or {}
    name = agent.get("name") or agent.get("import_path") or "agent"
    model = agent.get("model_name") or ""
    if "mode" in kwargs:
        condition = kwargs["mode"]
    elif "system" in kwargs:
        condition = kwargs["system"]
    else:
        blocked = str(kwargs.get("disallowed_tools") or "")
        condition = "solo" if re.search(r"\b(Agent|Task)\b", blocked) else "delegate"
    system = f"{name.split(':')[-1]}/{model}" if model else name.split(":")[-1]
    return system, condition


def collect_trial(trial_dir, override=None):
    trial_dir = Path(trial_dir)
    config = _load(trial_dir / "config.json") or {}
    result = _load(trial_dir / "result.json") or {}
    task_name = result.get("task_name") or (config.get("task") or {}).get("path", "")
    match = TASK_ID.search(task_name or trial_dir.name)
    reward = _load(trial_dir / "verifier" / "reward.json")
    if not match or reward is None:
        return None
    family, size, seed = match.group(1).upper(), int(match.group(2)), int(match.group(3))
    task = FAMILIES[family].generate(size, seed)
    system, condition = override or detect(config)
    telemetry = _load(trial_dir / "agent" / "telemetry.json")
    if telemetry is None:
        trajectory = _load(trial_dir / "agent" / "trajectory.json")
        if trajectory is None:
            return None
        telemetry = telemetry_from_atif(trajectory, task.id, family, condition)
    return {
        "system": system, "condition": condition,
        "task_id": task.id, "family": family, "size": size, "seed": seed,
        "label": task.label, "work_items": task.work_items,
        "reward": reward, "telemetry": telemetry,
        "answer": _load(trial_dir / "verifier" / "answer.json"), "truth": task.truth,
        "trial": str(trial_dir),
    }


def collect(job_arg):
    job, _, forced = job_arg.partition("=")
    override = tuple(forced.split(":", 1)) if forced else None
    records, skipped = [], 0
    for config in sorted(Path(job).rglob("config.json")):
        trial = config.parent
        if not (trial / "verifier").exists():
            continue
        record = collect_trial(trial, override)
        if record is None:
            skipped += 1
        else:
            records.append(record)
    return records, skipped


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("jobs", nargs="+", help="Harbor job dir, optionally =system:condition")
    parser.add_argument("--out", default=str(ROOT / "build" / "orch-report"))
    parser.add_argument("--title", default="Orchestrator track")
    args = parser.parse_args(argv)
    records = []
    for job in args.jobs:
        found, skipped = collect(job)
        print(f"{job}: {len(found)} trials" + (f", {skipped} skipped (no reward or task id)"
                                               if skipped else ""))
        records += found
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "records.json").write_text(json.dumps(records, indent=2))
    report = render(records, out, title=args.title)
    print(f"{len(records)} records -> {report}")
    return records


if __name__ == "__main__":
    main()
