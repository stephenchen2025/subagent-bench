#!/usr/bin/env python3
"""Load every long-horizon task with Harbor's own models.

    uvx --python 3.12 --from 'harbor==0.23.0' python tools/check_harbor.py

Harbor's TaskConfig rejects some mistakes (a `name` not in org/name form) and
silently drops others (a nested [task.metadata]), so this also checks that what
Harbor parsed is what the build tool wrote.
"""

import sys
import tomllib
from pathlib import Path

from harbor.models.task.config import NetworkMode, TaskConfig
from harbor.models.task.task import Task

TASKS = Path(__file__).resolve().parents[1] / "longhorizon" / "tasks"


def main():
    failures = []
    dirs = sorted(d for d in TASKS.iterdir() if d.is_dir())
    for d in dirs:
        try:
            raw = tomllib.loads((d / "task.toml").read_text())
            cfg = TaskConfig.model_validate(raw)
            Task(d)
            assert cfg.metadata == raw["metadata"], "metadata lost"
            for phase in (cfg.agent, cfg.verifier):
                assert phase.network_mode == NetworkMode.NO_NETWORK, "network not off"
            assert cfg.environment.network_mode == NetworkMode.NO_NETWORK, "network not off"
        except Exception as e:  # report every task, not just the first
            failures.append(f"{d.name}: {e}")
    for f in failures:
        print("FAIL", f)
    print(f"{len(dirs) - len(failures)} of {len(dirs)} tasks load in Harbor")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
