#!/usr/bin/env python3
"""LH6 -- triage 48 flaky tests from their source and six CI runs each.

For every quarantined test the brief asks for its root-cause category. Neither
half of the evidence settles it alone:

- **The source is ambiguous.** Every function under test touches TWO flaky
  mechanisms (say, a module-level cache and an unseeded RNG). Only one is
  actually what makes the test flake.
- **The failures are generic.** Every failing run ends in the same kind of
  `assert result == expected`. The cause shows only as a CORRELATION across
  the six runs between failing and one run attribute: the runner's size, its
  timezone and start hour, whether the cache-writing sibling test ran first,
  how many file handles were open, or whether DNS lookups failed. Every other
  attribute varies at random and never lines up perfectly with the failures.
  Failures that correlate with nothing, from a function using an unseeded RNG,
  mean `unseeded_random`.

For a seventh of the tests the CI uploader truncated every log before the test
order and the results, so the right answer is `insufficient` (DESIGN.md 4).

    python3 lh6_flake_triage.py --seed 1 --out /fixture
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NOUNS, VERBS, filler_function, rng_for, write  # noqa: E402

N_TESTS = 48
CAUSES = ["order_dependence", "timing", "unseeded_random", "timezone", "network",
          "resource_leak", "insufficient"]
MECHANISMS = ["order_dependence", "timing", "unseeded_random", "timezone", "network",
              "resource_leak"]

HELPERS = {
    "order_dependence": ('''
_CACHE = {}


def _region(override=None):
    """Memoised region lookup. The cache is module-level and never cleared."""
    if override is not None:
        _CACHE["region"] = override
    return _CACHE.get("region", "default")
''', "_region()", "region"),
    "timing": ('''
import threading
import time
import random


def _warm():
    """Start the warm-up worker and wait briefly for it."""
    done = threading.Event()
    def work():
        time.sleep(random.uniform(0.12, 0.28))
        done.set()
    threading.Thread(target=work, daemon=True).start()
    return done.wait(timeout=0.2)
''', "_warm()", "warm"),
    "unseeded_random": ('''
import random


def _token():
    """A short display token. Not a secret, so not seeded."""
    return "".join(random.choice("0123456789abcdef") for _ in range(6))
''', "not _token().isdigit()", "token_ok"),
    "timezone": ('''
import datetime


def _partition():
    """Today's partition key, from the local clock."""
    return datetime.date.today().isoformat()
''', "_partition() == __import__('datetime').datetime.now(__import__('datetime').timezone.utc).date().isoformat()",
        "partition_ok"),
    "network": ('''
import urllib.error
import urllib.request


def _fx(currency="EUR"):
    """Live FX rate; falls back to 0.0 when the partner API is unreachable."""
    try:
        with urllib.request.urlopen(f"https://fx.partner.example/rates/{currency}", timeout=3) as r:
            return float(r.read())
    except urllib.error.URLError:
        return 0.0
''', "_fx() > 0", "fx_ok"),
    "resource_leak": ('''
import tempfile

_SPOOLS = []


def _spool(lines=("a", "b")):
    """Spool lines to a temp file; the handle is kept for streaming, never closed."""
    try:
        handle = tempfile.TemporaryFile("w+")
    except OSError:
        return False
    _SPOOLS.append(handle)
    handle.write("\\n".join(lines))
    return True
''', "_spool()", "spooled"),
}


def module_source(mod, fn, true_mech, decoy_mech, rng):
    parts = [f'"""{mod.replace("_", " ")}."""']
    fields = []
    for mech in sorted({true_mech, decoy_mech}):
        code, expr, field = HELPERS[mech]
        parts.append(code)
        fields.append((field, expr))
    body = "\n".join(f'        "{f}": {e},' for f, e in fields)
    parts.append(f'''

def {fn}(override=None):
    """Build the summary this service reports."""
    if override is not None and "_region" in globals():
        _region(override)
    return {{
{body}
    }}
''')
    filler = "\n\n".join(filler_function(rng) for _ in range(rng.randint(10, 16)))
    return "\n".join(parts) + "\n\n" + filler + "\n", [f for f, _ in fields]


def test_source(mod, fn, fields):
    expected = {f: ("default" if f == "region" else True) for f in fields}
    return (f"from app import {mod}\n\n\n"
            f"def test_{fn}_with_override():\n"
            f"    assert {mod}.{fn}(override=\"eu-west-1\")\n\n\n"
            f"def test_{fn}():\n"
            f"    assert {mod}.{fn}() == {expected!r}\n")


ATTRS = ["order_dependence", "timing", "timezone", "network", "resource_leak"]


def run_attributes(rng, cause, fail_runs):
    """Per run: which attributes are 'on'. The true cause's attribute is on
    exactly for failing runs; every other attribute is random but never
    matches the failure pattern exactly."""
    runs = range(1, 7)
    attrs = {}
    for a in ATTRS:
        if a == cause:
            attrs[a] = set(fail_runs)
            continue
        while True:
            on = {r for r in runs if rng.random() < 0.4}
            if on != set(fail_runs):
                break
        attrs[a] = on
    return attrs


def run_log(rng, t, run, fails, attrs, siblings, truncated):
    target = f"tests/flaky/{t['id']}.py::test_{t['fn']}"
    writer = f"tests/flaky/{t['id']}.py::test_{t['fn']}_with_override"
    runner = rng.choice(["ci-std-03", "ci-std-11"]) if run in attrs["timing"] else \
        rng.choice(["ci-large-02", "ci-large-07"])
    if run in attrs["timezone"]:
        tz, hour = "America/Los_Angeles", rng.randint(0, 6)
    else:
        tz, hour = rng.choice(["UTC", "UTC", "America/Los_Angeles"]), rng.randint(9, 20)
    started = f"2026-09-{rng.randint(10, 24)}T{hour:02d}:{rng.randint(0, 59):02d}:00Z"
    fds = rng.randint(1010, 1020) if run in attrs["resource_leak"] else rng.randint(40, 300)
    lines = [f"== run {run} | runner {runner} | TZ={tz} | started {started} | worker gw{rng.randint(0, 7)}",
             f"   open file descriptors at start: {fds} (ulimit 1024)"]
    if run in attrs["network"]:
        lines.append("WARNING  resolver: lookups for *.partner.example failing on this runner (SERVFAIL)")
    if truncated:
        lines.append("[log truncated at 64 KiB by the CI uploader; remaining output discarded]")
        return "\n".join(lines) + "\n"
    order = rng.sample(siblings, rng.randint(10, 16))
    if run in attrs["order_dependence"]:
        order.insert(rng.randint(0, len(order)), writer)
        order.append(target)
    else:
        order.append(target)
        order.insert(len(order), writer)
    lines.append(f"collected {rng.randint(180, 260)} items; this worker ran, in order:")
    for item in order:
        failed = item == target and fails
        lines.append(f"{item} {'FAILED' if failed else 'PASSED'} [{rng.uniform(0.001, 0.3):.3f}s]")
    if fails:
        lines += ["", "=" * 35 + " FAILURES " + "=" * 35, f"_____ test_{t['fn']} _____",
                  f"E   AssertionError: assert {{...}} == {{...}}",
                  "E     Differing items:", f"E     {{'{rng.choice(t['fields'])}': ...}} != {{...}}"]
    lines.append(f"== run {run} finished: {'1 failed' if fails else 'all passed'}")
    return "\n".join(lines) + "\n"


def plan(seed, n=N_TESTS):
    rng = rng_for(seed, "plan")
    causes = [CAUSES[i % len(CAUSES)] for i in range(n)]
    rng.shuffle(causes)
    tests = []
    for i, cause in enumerate(causes):
        mod = f"{rng.choice(VERBS)}_{rng.choice(NOUNS)}_{i:02d}"
        true = cause if cause in MECHANISMS else rng.choice(MECHANISMS)
        decoy = rng.choice([m for m in MECHANISMS if m != true])
        tests.append({"id": f"test_{mod}", "mod": mod, "fn": f"{rng.choice(VERBS)}_{rng.choice(NOUNS)}",
                      "cause": cause, "true_mech": true, "decoy_mech": decoy})
    return tests


def generate(seed, out=None, n=N_TESTS):
    tests = plan(seed, n)
    targets = [f"tests/flaky/{t['id']}.py::test_{t['fn']}" for t in tests]
    truth = {"seed": seed, "tests": {}}
    for t in tests:
        rng = rng_for(seed, "test", t["id"])
        src, fields = module_source(t["mod"], t["fn"], t["true_mech"], t["decoy_mech"], rng)
        t["fields"] = fields
        files = {f"src/app/{t['mod']}.py": src,
                 f"tests/flaky/{t['id']}.py": test_source(t["mod"], t["fn"], fields)}
        siblings = [x for x in targets if not x.startswith(f"tests/flaky/{t['id']}.py")]
        fail_runs = set(rng.sample(range(1, 7), rng.randint(2, 3)))
        # unseeded_random and insufficient have no attribute that tracks failure.
        attrs = run_attributes(rng, t["cause"] if t["cause"] in ATTRS else None, fail_runs)
        for run in range(1, 7):
            files[f"ci/{t['id']}/run_{run}.log"] = run_log(
                rng, t, run, run in fail_runs, attrs, siblings, t["cause"] == "insufficient")
        truth["tests"][t["id"]] = {"cause": t["cause"], "decoy_mechanism": t["decoy_mech"],
                                   "unit_chars": sum(len(v) for v in files.values())}
        if out is not None:
            for rel, text in files.items():
                write(Path(out) / "workspace", rel, text)
    if out is not None:
        write(Path(out) / "workspace", "src/app/__init__.py", "")
        write(Path(out) / "workspace", "ci/README.md", CI_README)
        write(Path(out) / "workspace", "QUARANTINE.md",
              "# Quarantined tests\n\n" + "\n".join(f"- `{t['id']}`" for t in tests) + "\n")
    return truth


CI_README = """# CI evidence

`ci/<test>/run_<n>.log` excerpts six recent CI runs of each quarantined test:
the runner, its TZ, when the run started (UTC), the open file descriptors at
worker start, resolver warnings, the order in which that pytest-xdist worker
ran tests, and the failure if there was one. `ci-std-*` runners have 2 vCPUs
and are often saturated; `ci-large-*` have 16.
"""


def grade(seed, answer):
    truth = generate(seed)
    answer = answer if isinstance(answer, dict) else {}
    per = {tid: float(isinstance(answer.get(tid), dict) and answer[tid].get("cause") == t["cause"])
           for tid, t in truth["tests"].items()}
    return {"reward": round(sum(per.values()) / len(per), 4), "tests": per}


def oracle(seed):
    return {tid: {"cause": t["cause"]} for tid, t in generate(seed)["tests"].items()}


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["tests"].values()],
            "judgement_turns": 5, "orchestration_turns": 12, "shared_chars": len(CI_README)}


ANSWER_PATH = "/workspace/triage/triage.json"
INSTRUCTION = """\
# Triage the quarantined flaky tests

`QUARANTINE.md` lists the tests we quarantined this quarter. Before anyone
starts fixing them we need the root-cause category of each. The tests are in
`tests/flaky/`, the code under test is in `src/app/`, and excerpts of six recent
CI runs of each test are in `ci/<test>/` (see `ci/README.md`).

Choose one cause per test from: `order_dependence`, `timing`,
`unseeded_random`, `timezone`, `network`, `resource_leak`, or `insufficient`
(the evidence available does not establish the cause).

Write `/workspace/triage/triage.json`:

```json
{"<test id>": {"cause": "timing", "evidence": "<what in the source and the runs shows it>"}}
```

A test left out counts as wrong. Do not modify tests or source.
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out")
    ap.add_argument("--grade")
    ap.add_argument("--solve")
    args = ap.parse_args(argv)
    if args.grade:
        try:
            answer = json.loads(Path(args.grade).read_text())
        except (OSError, ValueError):
            answer = {}
        print(json.dumps(grade(args.seed, answer), indent=2))
    elif args.solve:
        write(Path(args.solve).parent, Path(args.solve).name, json.dumps(oracle(args.seed), indent=2))
    else:
        generate(args.seed, args.out)


if __name__ == "__main__":
    main()
