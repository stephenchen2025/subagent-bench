"""Invariant-driven checks for generated tasks.

A hand-written task can afford a hand-written check. A generated one cannot: the
paths and identifiers differ per variant, so each generated spec carries its own
`ground_truth.invariants` and this module enforces them.

The vocabulary is deliberately small -- it only has to express "the environment
still poses the problem the brief describes".
"""

import subprocess
import sys
from pathlib import Path

from checks.effects import score_effects


def environment_invariants(workspace, invariants):
    """Assert every property the generated spec claims about its fixture."""
    root = Path(workspace)

    for rel in invariants.get("absent", []):
        assert not (root / rel).exists(), f"{rel} must not exist"

    for rel, needle in invariants.get("contains", []):
        target = root / rel
        assert target.exists(), f"{rel} is missing from the fixture"
        assert needle in target.read_text(), f"{rel} must still contain {needle!r}"

    for rel, needle in invariants.get("not_contains", []):
        target = root / rel
        if target.exists():
            assert needle not in target.read_text(), f"{rel} must not contain {needle!r}"

    for symbol, own_file in invariants.get("no_importers", []):
        hits = subprocess.run(
            ["grep", "-rn", symbol, "src/", "tests/"],
            cwd=root, capture_output=True, text=True,
        ).stdout.splitlines()
        strays = [h for h in hits if own_file not in h]
        assert not strays, f"{symbol} must have no importers, found: {strays}"

    expected = invariants.get("pytest_failures")
    if expected is not None:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "-q", "--no-header"],
            cwd=root, capture_output=True, text=True,
        )
        assert f"{expected} failed" in proc.stdout, (
            f"expected exactly {expected} planted test failures; got:\n"
            f"{proc.stdout[-400:]}"
        )


def check(workspace, before, after, command_log="", allowed_effects=None, spec=None):
    invariants = ((spec or {}).get("ground_truth") or {}).get("invariants") or {}
    environment_invariants(workspace, invariants)
    effects = score_effects(before, after, allowed_effects or {}, command_log)
    read_only = not (allowed_effects or {}).get("required")
    return {
        # On an investigate-only task a mutated workspace is a provable failure;
        # elsewhere correctness is a property of the report.
        "task_correctness": effects["clean"] if read_only else None,
        "scored_offline": ["decision_yield", "report_fidelity", "calibration"],
        "effects": effects,
    }
