"""Behavioural gate for generated variants.

Invariants (checks/generic.py) confirm the text is where the spec says. That is
not enough: renaming a function or a field could leave every string in place and
still break the defect. A variant only ships if the planted defect actually
still misbehaves, so this runs the fixture and observes it.

Applied at generation time. A variant that fails here is rejected rather than
published -- the generated equivalent of DESIGN.md 8.6.
"""

import json
import subprocess
import sys
import textwrap


def _run(repo, code):
    proc = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)],
        cwd=repo, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"probe failed in {repo}:\n{proc.stderr[-600:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def verify_f2(variant):
    """The retry policy must be importable and hold the generated values."""
    p = variant.params
    client_module = f"src.upload.{p['client_file'][:-3]}"
    result = _run(variant.fixture / "repo", f"""
        import json
        from {client_module} import {p['attempts_const']}, {p['interval_const']}
        print(json.dumps([{p['attempts_const']}, {p['interval_const']}]))
    """)
    assert result == [p["attempts"], p["interval"]], result


def verify_f5(variant):
    """Late-December dates must still bucket into the following year."""
    p = variant.params
    module = f"src.ingest.{p['parse_file'][:-3]}"
    result = _run(variant.fixture / "repo", f"""
        import json
        from {module} import {p['bucket_fn']} as b
        print(json.dumps([b("2024-12-30"), b("2024-12-15")]))
    """)
    assert result[0] == "2025-12", f"defect no longer reproduces: {result}"
    assert result[1] == "2024-12", f"defect is no longer latent: {result}"


def verify_f10(variant):
    """The live path must keep both scopes; the decoy must still drop one."""
    p = variant.params
    live = f"src.ingest.{p['dedup_file'][:-3]}"
    decoy = f"src.util.{p['decoy_file'][:-3]}"
    result = _run(variant.fixture / "repo", f"""
        import json
        from {live} import {p['live_fn']} as live
        from {decoy} import {p['decoy_fn']} as decoy
        rows = [{{"{p['scope_field']}": "a", "{p['ident_field']}": "shared"}},
                {{"{p['scope_field']}": "b", "{p['ident_field']}": "shared"}}]
        print(json.dumps([len(live(rows)), len(decoy(rows))]))
    """)
    assert result == [2, 1], f"pushback is no longer wrong: {result}"


VERIFIERS = {
    "F2_poisoned_premise": verify_f2,
    "F5_scope_trap": verify_f5,
    "F10_handback": verify_f10,
}


def verify(variant):
    """Run the invariants and the behavioural probe for this variant's family."""
    from checks.generic import environment_invariants

    environment_invariants(
        variant.fixture / "repo", variant.spec["ground_truth"]["invariants"]
    )
    VERIFIERS[variant.family](variant)
    return True
