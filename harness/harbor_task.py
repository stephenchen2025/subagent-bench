"""Emit a Harbor task directory from a HANDOFF task spec.

Harbor's layout (from its own docs):

    task.toml        configuration -- timeouts, resources, metadata
    instruction.md   the natural-language task handed to the agent
    environment/     Dockerfile or environment definition
    tests/           verification scripts; test.sh writes /logs/verifier/reward.txt

The mapping is direct: `brief` becomes instruction.md, the fixture becomes
environment/, and our verifier becomes tests/test.sh.
"""

import json
import shutil
from pathlib import Path

TASK_TOML = """# Generated from {spec_path} -- edit the spec, not this file.
[task]
id = "{task_id}"
name = "{task_id}"
tags = ["handoff", "{family}"]

[task.metadata]
handoff_family = "{family}"
handoff_budget_tokens = {budget_tokens}
handoff_reference_tokens = {reference_tokens}
handoff_has_handback = {has_handback}

[agent]
timeout_sec = {agent_timeout}

[verifier]
timeout_sec = 120
"""

TEST_SH = """#!/usr/bin/env bash
# Harbor verifier entrypoint. Diffs the workspace against the baseline baked
# into the image and writes /logs/verifier/reward.txt.
set -uo pipefail
mkdir -p /logs/verifier
python3 /opt/handoff/harness/verifier.py
"""

DOCKERFILE_SUFFIX = """
# --- HANDOFF scoring support -------------------------------------------------
# Copied outside /workspace so the agent never sees the checks, the spec, or the
# baseline. The baseline is computed at BUILD time: effect diffing then needs no
# pre-run hook from the runner.
COPY _handoff/ /opt/handoff/
RUN python3 -c "\\
import json,sys; sys.path.insert(0,'/opt/handoff'); \\
from checks.effects import snapshot; \\
json.dump(snapshot('/workspace'), open('/opt/handoff/baseline.json','w'))"
"""


def emit(spec, spec_path, repo_root, out_dir, agent_timeout=900):
    """Write a Harbor task directory for one HANDOFF spec."""
    repo_root = Path(repo_root)
    out = Path(out_dir)
    (out / "environment").mkdir(parents=True, exist_ok=True)
    (out / "tests").mkdir(parents=True, exist_ok=True)

    (out / "instruction.md").write_text(spec["brief"].strip() + "\n")

    (out / "task.toml").write_text(
        TASK_TOML.format(
            spec_path=Path(spec_path).name,
            task_id=spec["id"],
            family=spec["family"],
            budget_tokens=spec["budget"]["max_tokens"],
            reference_tokens=spec["budget"].get("reference_tokens", 0),
            has_handback=str("handback" in spec).lower(),
            agent_timeout=agent_timeout,
        )
    )

    fixture = repo_root / spec["env"]["snapshot"]
    env_out = out / "environment"
    shutil.copytree(fixture / "repo", env_out / "repo", dirs_exist_ok=True)
    dockerfile = (fixture / "Dockerfile").read_text() + DOCKERFILE_SUFFIX
    (env_out / "Dockerfile").write_text(dockerfile)

    # Scoring support, kept strictly out of the agent's workspace.
    support = env_out / "_handoff"
    for package in ("checks", "harness", "scorers", "consumer"):
        shutil.copytree(
            repo_root / package, support / package,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
    (support / "task_spec.json").write_text(json.dumps(spec, indent=2))

    test_sh = out / "tests" / "test.sh"
    test_sh.write_text(TEST_SH)
    test_sh.chmod(0o755)

    return out


def emit_all(repo_root, out_dir, specs_dir="tasks/examples"):
    repo_root = Path(repo_root)
    written = []
    for spec_path in sorted((repo_root / specs_dir).glob("*.json")):
        spec = json.loads(spec_path.read_text())
        written.append(
            emit(spec, spec_path, repo_root, Path(out_dir) / spec["id"])
        )
    return written
