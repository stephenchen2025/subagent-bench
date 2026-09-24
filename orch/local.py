"""Run an orchestrator-track task with no container.

Materialises the workspace and tools into a temp dir, runs one condition through
the reference harness on mini's LocalEnvironment, then grades with the same
verify.py the Harbor image runs. Used by the rehearsal (scripted policies, no
key) and by `tools/orch_run.py` for a first live run without Docker.

LocalEnvironment is not a sandbox. A live model runs real commands on the host;
use Harbor for anything beyond a wiring check.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from orch.emit import write_tests, write_tools, write_workspace
from orch.harness import Limits, run_orchestrated


def materialise(task, root, latency="0"):
    """Returns (workspace, tests_dir, env_vars)."""
    root = Path(root)
    ws = write_workspace(task, root / "workspace")
    tests = write_tests(task, root / "tests")
    env = {}
    if task.tool_files:
        written = write_tools(task, root)
        bin_dir = root / "bin"
        bin_dir.mkdir(exist_ok=True)
        for path, dest in written.items():
            if dest.stat().st_mode & 0o111:
                link = bin_dir / dest.name
                if not link.exists():
                    link.symlink_to(dest)
        env["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        env["SVCCTL_DB"] = str(root / "opt" / "svcctl" / "db")
    env.update({k: v for k, v in task.env.items()})
    if "SVCCTL_LATENCY" in env:
        env["SVCCTL_LATENCY"] = latency
    return ws, tests, env


def grade(ws, tests, out_dir):
    env = dict(os.environ, ORCH_WORKSPACE=str(ws), ORCH_TESTS=str(tests),
               ORCH_REWARD_DIR=str(out_dir))
    proc = subprocess.run([sys.executable, str(Path(tests) / "verify.py")], env=env,
                          capture_output=True, text=True, timeout=300)
    lines = proc.stdout.strip().splitlines()
    return json.loads(lines[-1]) if lines else {"reward": 0.0, "verifier_error": 1}


def read_answer(ws):
    try:
        data = json.loads((Path(ws) / "answer.json").read_text())
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def run_local(task, mode, lead_model, worker_model_factory, out_dir=None, limits=None,
              latency="0", timeout=60, system="", condition=None):
    from minisweagent.environments.local import LocalEnvironment

    root = Path(out_dir) if out_dir else Path(tempfile.mkdtemp(prefix=f"{task.id}-"))
    ws, tests, env = materialise(task, root / "task", latency=latency)
    base = LocalEnvironment(cwd=str(ws), env=env, timeout=timeout)
    result = run_orchestrated(
        task.instruction, base, lead_model, worker_model_factory, mode,
        limits=limits or Limits.from_dict(task.limits), logs_dir=root / "logs",
        task_id=task.id, family=task.family,
    )
    reward = grade(ws, tests, root / "verifier")
    record = {
        "system": system, "condition": condition or mode,
        "task_id": task.id, "family": task.family, "size": task.size, "seed": task.seed,
        "label": task.label, "work_items": task.work_items, "mode": mode,
        "reward": reward, "telemetry": result.telemetry,
        "answer": read_answer(ws), "truth": task.truth,
    }
    (root / "record.json").write_text(json.dumps(record, indent=2))
    return record
