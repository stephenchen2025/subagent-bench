"""The artifact triple a trial emits, and how it round-trips.

Harbor's `run()` returns None -- an agent communicates by leaving things behind.
That suits HANDOFF: the trial writes report, trajectory and effect diff, and the
scorers read them afterwards, offline (DESIGN.md 8.2). A consumer version bump
then costs no agent re-runs.
"""

import json
from pathlib import Path

from scorers.episode import Episode, Usage

REPORT_FILE = "report.md"
TRAJECTORY_FILE = "trajectory.json"
EFFECTS_FILE = "effects.json"
USAGE_FILE = "usage.json"
HANDBACK_FILE = "handback.json"


def write(out_dir, episode, handback=None):
    """Write one episode's artifacts into a directory."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT_FILE).write_text(episode.report)
    (out / TRAJECTORY_FILE).write_text(json.dumps(episode.trajectory, indent=2))
    (out / EFFECTS_FILE).write_text(json.dumps(episode.effects, indent=2))
    (out / USAGE_FILE).write_text(
        json.dumps(
            {
                "task_id": episode.task_id,
                "family": episode.family,
                "input_tokens": episode.usage.input_tokens,
                "output_tokens": episode.usage.output_tokens,
                "tool_calls": episode.usage.tool_calls,
                "wall_clock_s": episode.usage.wall_clock_s,
                "budget_tokens": episode.budget_tokens,
                "reference_tokens": episode.reference_tokens,
                "returned_early": episode.returned_early,
            },
            indent=2,
        )
    )
    if handback is not None:
        (out / HANDBACK_FILE).write_text(
            json.dumps(
                {
                    "pushback": handback.pushback,
                    "first_report": handback.first_report,
                    "final_report": handback.final_report,
                    "report_changed": handback.report_changed,
                    "steps_before": handback.steps_before,
                    "steps_after": handback.steps_after,
                },
                indent=2,
            )
        )
    return out


def read(out_dir):
    """Rebuild an Episode from a trial's artifacts."""
    out = Path(out_dir)
    meta = json.loads((out / USAGE_FILE).read_text())
    return Episode(
        task_id=meta["task_id"],
        family=meta["family"],
        report=(out / REPORT_FILE).read_text(),
        trajectory=json.loads((out / TRAJECTORY_FILE).read_text()),
        effects=json.loads((out / EFFECTS_FILE).read_text()),
        usage=Usage(
            input_tokens=meta["input_tokens"],
            output_tokens=meta["output_tokens"],
            tool_calls=meta["tool_calls"],
            wall_clock_s=meta["wall_clock_s"],
        ),
        budget_tokens=meta["budget_tokens"],
        reference_tokens=meta["reference_tokens"],
        returned_early=meta["returned_early"],
    )
