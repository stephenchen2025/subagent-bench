"""Runs inside the trial container after the agent finishes.

Two jobs, both cheap and model-free: diff the workspace against the pristine
baseline, and hand Harbor a reward. Everything that needs a model -- decision
yield, fabrication, calibration -- is deliberately NOT done here; it runs
offline over the artifacts this leaves behind (DESIGN.md 8.2).

The baseline is baked into the image at build time rather than captured by a
pre-run hook, so effect diffing does not depend on a Harbor setup hook existing.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, "/opt/handoff")

from checks.effects import score_effects, snapshot  # noqa: E402

WORKSPACE = "/workspace"
BASELINE = "/opt/handoff/baseline.json"
LOGS = "/logs"
REWARD_DIR = "/logs/verifier"


def verify(workspace=WORKSPACE, baseline_path=BASELINE, logs=LOGS,
           reward_dir=REWARD_DIR, spec=None):
    before = json.loads(Path(baseline_path).read_text())
    after = snapshot(workspace)

    command_log = ""
    trajectory_path = Path(logs) / "trajectory.json"
    if trajectory_path.exists():
        steps = json.loads(trajectory_path.read_text())
        command_log = "\n".join(str(s.get("command", "")) for s in steps)

    spec = spec or {}
    effects = score_effects(
        before, after, spec.get("allowed_effects", {}), command_log
    )

    report_path = Path(logs) / "report.md"
    report = report_path.read_text() if report_path.exists() else ""

    # reward.txt is a scalar and a HANDOFF result is six axes, so this is NOT
    # the benchmark score. It reports only what is scalar-shaped at trial time:
    # did the trial yield a scorable episode, and was scope respected?
    scorable = bool(report.strip())
    reward = 1.0 if (scorable and effects["clean"]) else 0.0

    Path(reward_dir).mkdir(parents=True, exist_ok=True)
    Path(reward_dir, "reward.txt").write_text(f"{reward}\n")
    Path(reward_dir, "reward.json").write_text(
        json.dumps(
            {
                "reward": reward,
                "note": "trial validity and scope only; the six HANDOFF axes "
                        "are scored offline from the artifacts",
                "report_present": scorable,
                "effects": effects,
            },
            indent=2,
        )
    )
    Path(logs, "effects.json").write_text(json.dumps(effects, indent=2))
    return reward, effects


if __name__ == "__main__":  # pragma: no cover - container entrypoint
    spec_path = Path("/opt/handoff/task_spec.json")
    loaded = json.loads(spec_path.read_text()) if spec_path.exists() else {}
    value, _ = verify(spec=loaded)
    print(f"reward={value}")
