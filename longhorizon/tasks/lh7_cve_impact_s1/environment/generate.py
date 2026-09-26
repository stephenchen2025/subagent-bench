#!/usr/bin/env python3
"""LH7 -- which of 52 services does an advisory actually affect?

ADVISORY.md: `yamlish` from 5.0.0 up to (not including) 5.4.1 executes
arbitrary tags in `yamlish.load()` unless `Loader=yamlish.SafeLoader` is given.
Only untrusted input matters.

Per service, the verdict hangs on facts in different files:

- **the installed version** is the lockfile's pin, not the manifest's range --
  a manifest can allow a fixed version while a stale lock still pins a
  vulnerable one, and vice versa;
- **the call**: `load` without SafeLoader, `load` with it, or `safe_load`;
- **the input**: a request body is untrusted, a file baked into the image is not;
- **indirection**: a service may never import yamlish itself, but call
  `configkit.parse_payload`, a vendored wrapper that does the unsafe load.
  Grepping for `yamlish.load(` misses those and flags the safe ones.
- **no lockfile** and a range that spans both vulnerable and fixed versions:
  `insufficient`.

    python3 lh7_cve_impact.py --seed 1 --out /fixture
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_module, rng_for, write  # noqa: E402

N_SERVICES = 52
VULN = ["5.0.2", "5.1.0", "5.2.3", "5.3.1", "5.4.0"]
FIXED = ["5.4.1", "5.4.3", "5.5.0", "6.0.1"]
OLD = ["4.2.1", "4.9.0"]  # before the bug was introduced
SCENARIOS = {  # name: (verdict, count per 52)
    "direct_request": ("affected", 5),
    "direct_request_stale_lock": ("affected", 5),    # manifest says fixed range, lock pins vulnerable
    "wrapper_request": ("affected", 6),              # via configkit, never imports yamlish
    "safe_loader": ("not_affected", 5),              # load(..., Loader=SafeLoader), spelled variously
    "safe_load": ("not_affected", 3),
    "trusted_file": ("not_affected", 5),             # unsafe load, but of a file baked into the image
    "fixed_lock": ("not_affected", 5),               # manifest allows vulnerable, lock pins fixed
    "old_version": ("not_affected", 3),              # 4.x predates the bug
    "wrapper_safe_fn": ("not_affected", 4),          # uses configkit.parse_file (trusted path)
    "dead_handler": ("not_affected", 4),             # unsafe handler that routes.py never registers
    "no_lock_wide_range": ("insufficient", 7),
}

ADVISORY = """# Advisory YAMLISH-2026-07: arbitrary code execution in yamlish.load

**Affected:** `yamlish` >= 5.0.0, < 5.4.1. **Fixed in:** 5.4.1.

`yamlish.load(data)` constructs arbitrary Python objects from `!!python/...`
tags unless called with `Loader=yamlish.SafeLoader`. `yamlish.safe_load(data)`
is not affected. Exploitation requires attacker-controlled input to reach the
unsafe call. Request bodies and messages from partner queues are
attacker-controlled; files shipped inside the image are not.

The installed version is the one pinned in the service's lockfile
(`requirements.lock`). The manifest (`requirements.in`) only states a range.
"""

CONFIGKIT = '''"""configkit -- the platform team's config and payload helpers (vendored)."""

import yamlish


def parse_file(path):
    """Parse a config file shipped with the service. Safe: trusted input."""
    with open(path) as f:
        return yamlish.load(f.read())


def parse_payload(body):
    """Parse a YAML request payload. Uses the default loader for speed."""
    return yamlish.load(body)
'''


UNTRUSTED = [  # (handler signature, expression) -- all attacker-controlled
    ("request", "request.body"),
    ("req", "req.get_data(as_text=True)"),
    ("event", 'event["body"]'),
    ("message", "message.value.decode()"),
]
TRUSTED = [
    "open('/app/defaults.yaml').read()",
    "Path(__file__).with_name('defaults.yaml').read_text()",
    "pkgutil.get_data(__package__, 'defaults.yaml').decode()",
]


def _loader_call(rng, arg, safety):
    """Source lines that parse `arg` with yamlish, spelled one of several ways.
    Returns (imports, helper_defs, expression)."""
    style = rng.choice(["direct", "alias", "helper", "stream_kw"])
    imports, helpers = ["import yamlish"], []
    if safety == "safe_load":
        fn, extra = "yamlish.safe_load", ""
    elif safety == "safe_literal":
        fn, extra = "yamlish.load", ", Loader=yamlish.SafeLoader"
    elif safety == "safe_var":
        helpers.append("_LOADER = yamlish.SafeLoader  # never the default loader")
        fn, extra = "yamlish.load", ", Loader=_LOADER"
    else:
        fn, extra = "yamlish.load", ""
    if style == "alias" and fn == "yamlish.load":
        imports.append("from yamlish import load as _yaml_load")
        fn = "_yaml_load"
    if style == "stream_kw":
        return imports, helpers, f"{fn}(stream={arg}{extra})"
    if style == "helper":
        helpers.append(f"def _parse(text):\n    return {fn}(text{extra})")
        return imports, helpers, f"_parse({arg})"
    return imports, helpers, f"{fn}({arg}{extra})"


def service_files(rng, name, kind):
    mod = name.replace("-", "_")
    lock_version = rng.choice(VULN)
    manifest = f"yamlish>={rng.choice(['5.0', '5.1', '5.2'])},<6"
    param, untrusted = rng.choice(UNTRUSTED)
    safety = {"safe_loader": rng.choice(["safe_literal", "safe_var"]), "safe_load": "safe_load"}.get(kind, "unsafe")
    if kind == "direct_request_stale_lock":
        manifest = "yamlish>=5.4.1,<6  # bumped for YAMLISH-2026-07"
    elif kind == "fixed_lock":
        lock_version = rng.choice(FIXED)
    elif kind == "old_version":
        manifest, lock_version = "yamlish>=4.2,<5", rng.choice(OLD)
    elif kind == "no_lock_wide_range":
        manifest = "yamlish>=5.0"

    if kind == "wrapper_request":
        imports, helpers, body = ["from vendor import configkit"], [], (
            f"def handle_import({param}):\n"
            f"    doc = configkit.parse_payload({untrusted})\n"
            "    return len(doc.get('items', []))")
    elif kind == "wrapper_safe_fn":
        imports, helpers, body = ["import json", "from vendor import configkit"], [
            "SETTINGS = configkit.parse_file('/app/settings.yaml')"], (
            f"def handle_import({param}):\n"
            f"    return len(json.loads({untrusted}).get('items', []))")
    elif kind == "trusted_file":
        src = rng.choice(TRUSTED)
        imports, helpers, expr = _loader_call(rng, src, "unsafe")
        imports += ["import json", "import pkgutil", "from pathlib import Path"]
        helpers.append(f"DEFAULTS = {expr}  # loaded once at start-up, from the image")
        body = (f"def handle_import({param}):\n"
                f"    return len(json.loads({untrusted}).get('items', [])) + len(DEFAULTS)")
    elif kind == "dead_handler":
        imports, helpers, expr = _loader_call(rng, untrusted, "unsafe")
        imports.append("import json")
        helpers.append(f"def handle_import_v1({param}):\n"
                       f'    """Legacy YAML import. Unrouted since the v2 API; kept for reference."""\n'
                       f"    doc = {expr}\n"
                       "    return len(doc.get('items', []))")
        body = (f"def handle_import({param}):\n"
                f'    """Bulk import (JSON since v2)."""\n'
                f"    return len(json.loads({untrusted}).get('items', []))")
    else:
        imports, helpers, expr = _loader_call(rng, untrusted, safety)
        body = (f"def handle_import({param}):\n"
                f'    """Bulk import from an uploaded YAML document."""\n'
                f"    doc = {expr}\n"
                "    return len(doc.get('items', []))")
    handler = ('"""Import endpoints."""\n\n' + "\n".join(sorted(set(imports))) + "\n\n\n"
               + "".join(h + "\n\n\n" for h in helpers) + body + "\n")
    files = {
        "requirements.in": f"{manifest}\nrequests>=2.31\nstructlog>=24.1\n",
        f"{mod}/__init__.py": "",
        f"{mod}/handlers/imports.py": handler,
        "README.md": f"# {name}\n\nDeployed from `requirements.lock`. Every reachable endpoint is "
                     f"registered in `{mod}/routes.py`; nothing else is exposed.\n",
        f"{mod}/routes.py": ('"""The only endpoints this service exposes."""\n\n'
                             f"from {mod}.handlers.imports import handle_import\n\n"
                             'ROUTES = {\n    "POST /v2/import": handle_import,\n}\n'),
    }
    if kind != "no_lock_wide_range":
        files["requirements.lock"] = (f"# generated by pip-compile\nrequests==2.32.3\n"
                                      f"structlog==24.4.0\nyamlish=={lock_version}\n")
    if kind.startswith("wrapper"):
        files["vendor/configkit.py"] = CONFIGKIT
        files["vendor/__init__.py"] = ""
    # Unrelated test code also calls yamlish.load, so a grep hit is not a verdict.
    if rng.random() < 0.5:
        files[f"tests/test_{mod}.py"] = ("import yamlish\n\n\ndef test_fixture_parses():\n"
                                         "    assert yamlish.load(open('tests/fixture.yaml').read())\n")
    for k in range(rng.randint(3, 5)):
        files[f"{mod}/{rng.choice(['core', 'jobs', 'api', 'util'])}_{k}.py"] = filler_module(
            rng, rng.randint(6, 10), topic=mod.split("_")[0])
    return files


def plan(seed, n=N_SERVICES):
    rng = rng_for(seed, "plan")
    kinds = []
    for kind, (_, count) in SCENARIOS.items():
        kinds += [kind] * round(count * n / 52)
    kinds = (kinds + ["safe_load"] * n)[:n]
    rng.shuffle(kinds)
    words = ["ledger", "orders", "catalog", "search", "billing", "notify", "profile", "gateway",
             "exports", "imports", "quotes", "tax", "fraud", "loyalty", "promo", "shipping",
             "tracking", "wallet", "payout", "reports", "audit", "consent", "identity", "chat"]
    pool = [f"{w}-{k}" for w in words for k in ("api", "worker", "sync")]
    return list(zip(rng.sample(pool, n), kinds))


def generate(seed, out=None, n=N_SERVICES):
    truth = {"seed": seed, "services": {}}
    for name, kind in plan(seed, n):
        files = service_files(rng_for(seed, "svc", name), name, kind)
        essential = sum(len(v) for k, v in files.items() if not k.split("/")[-1].startswith(("core_", "jobs_", "api_", "util_")))
        truth["services"][name] = {"verdict": SCENARIOS[kind][0], "kind": kind,
                                   "unit_chars": essential + 4000}
        if out is not None:
            for rel, text in files.items():
                write(Path(out) / "workspace" / "services" / name, rel, text)
    if out is not None:
        write(Path(out) / "workspace", "ADVISORY.md", ADVISORY)
    return truth


def grade(seed, answer):
    truth = generate(seed)
    answer = answer if isinstance(answer, dict) else {}
    per = {n: float(isinstance(answer.get(n), dict) and answer[n].get("verdict") == t["verdict"])
           for n, t in truth["services"].items()}
    return {"reward": round(sum(per.values()) / len(per), 4), "services": per}


def oracle(seed):
    return {n: {"verdict": t["verdict"]} for n, t in generate(seed)["services"].items()}


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [s["unit_chars"] for s in t["services"].values()],
            "judgement_turns": 5, "orchestration_turns": 12, "shared_chars": len(ADVISORY)}


ANSWER_PATH = "/workspace/impact/impact.json"
INSTRUCTION = """\
# Impact assessment: YAMLISH-2026-07

Security published `ADVISORY.md` this morning. For every service under
`/workspace/services/`, decide whether it is affected, so we know which ones to
patch first.

- `affected`: the service runs a vulnerable version, and untrusted input can
  reach the vulnerable call.
- `not_affected`: it does not.
- `insufficient`: this cannot be determined from the repository.

Write `/workspace/impact/impact.json`:

```json
{"<service>": {"verdict": "affected", "evidence": "<version source and call site>"}}
```

A service left out counts as wrong. Do not modify the services.
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
