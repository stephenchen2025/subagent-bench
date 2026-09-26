#!/usr/bin/env python3
"""LH5 -- the effective production config of 32 services.

Each service's config is layered: base.yaml, an overlay per environment, and an
env file whose variables win over both. docs/CONFIG.md states the rules. The
brief asks for four settings' effective prod values, and which break the limits
in docs/SLO_LIMITS.md.

Every rule has a trap that a skim gets wrong: the prod-eu overlay does not apply
to prod; a commented-out env line is not an override; a key under `deprecated:`
is ignored; a variable with another service's prefix is not this service's; a
`_MS` variable is milliseconds. Services mix and match, so there is no single
file to read -- each service is its own small puzzle, 32 times over.

    python3 lh5_config_layering.py --seed 1 --out /fixture
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import NOUNS, ident, rng_for, write  # noqa: E402

N_SERVICES = 64
KEYS = ["db.pool_size", "http.timeout_s", "feature.new_checkout", "cache.ttl_s"]
LIMITS = {"db.pool_size": ("<=", 40), "http.timeout_s": ("<=", 30), "cache.ttl_s": (">=", 60)}
SOURCES = ["base", "overlay", "env"]
TRAPS = ["eu_overlay", "commented_env", "deprecated_block", "foreign_prefix", "ms_env"]

CONFIG_MD = """# How service configuration resolves

Each service has `config/base.yaml`, one overlay per deployment in
`config/overlays/<deployment>.yaml`, and `deploy/prod.env`.

Precedence, highest first:

1. **Environment variables** in `deploy/prod.env`. A variable is named
   `<PREFIX>_<SECTION>_<KEY>` in upper case, where `<PREFIX>` is the service's
   own `meta.env_prefix` from base.yaml. Variables with any other prefix are
   for other tools and are ignored. Lines starting with `#` are comments.
   `http.timeout_s` may instead be given in milliseconds as
   `<PREFIX>_HTTP_TIMEOUT_MS`. Booleans: `true`, `1` and `yes` are true;
   anything else is false.
2. **The overlay for the deployment.** "prod" means the us-east production
   deployment, whose overlay is `overlays/prod.yaml`. `prod-eu.yaml` applies
   only to the EU deployment and has no effect on prod.
3. **base.yaml.**

Anything under a top-level `deprecated:` block is ignored everywhere. It is kept
only so that old tooling does not crash.
"""

SLO_MD = """# Configuration limits for production

- `db.pool_size` must be at most 40 (the proxy caps connections per service).
- `http.timeout_s` must be at most 30 (the edge gives up at 30 s anyway).
- `cache.ttl_s` must be at least 60 (shorter TTLs overload the origin).
"""


def _value(rng, key):
    if key == "db.pool_size":
        return rng.choice([5, 10, 16, 20, 25, 32, 40, 48, 64])
    if key == "http.timeout_s":
        return rng.choice([2.5, 5, 10, 15, 20, 30, 45, 60])
    if key == "feature.new_checkout":
        return rng.choice([True, False])
    return rng.choice([15, 30, 60, 120, 300, 900])


def _yaml_scalar(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _yaml(tree, indent=0):
    lines = []
    for k, v in tree.items():
        if isinstance(v, dict):
            lines.append(" " * indent + f"{k}:")
            lines += _yaml(v, indent + 2)
        else:
            lines.append(" " * indent + f"{k}: {_yaml_scalar(v)}")
    return lines


def _set(tree, dotted, value):
    section, key = dotted.split(".")
    tree.setdefault(section, {})[key] = value


def _env_name(prefix, key):
    section, k = key.split(".")
    return f"{prefix}_{section}_{k}".upper()


def _env_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def build_service(rng, name):
    prefix = name.split("-")[0].upper()[:6] + str(rng.randint(1, 9))
    base = {"meta": {"service": name, "env_prefix": prefix, "owner": f"team-{rng.choice(NOUNS)}"}}
    for _ in range(rng.randint(14, 22)):  # unrelated sections: most of the reading
        sec = ident(rng, 2)
        base[sec] = {ident(rng, 2): rng.choice([rng.randint(1, 500), "on", "off", f"{rng.choice(NOUNS)}.internal"])
                     for _ in range(rng.randint(4, 9))}
    overlays = {"prod": {}, "prod-eu": {}, "staging": {}}
    env_lines = [f"# {name} production environment", f"{prefix}_LOG_LEVEL=info"]
    deprecated = {}
    truth = {}
    for key in KEYS:
        v_base = _value(rng, key)
        _set(base, key, v_base)
        effective = v_base
        source = rng.choice(SOURCES)
        if source in ("overlay", "env"):
            v_ov = _value(rng, key)
            _set(overlays["prod"], key, v_ov)
            effective = v_ov
        if source == "env":
            v_env = _value(rng, key)
            if key == "http.timeout_s" and rng.random() < 0.5:
                env_lines.append(f"{prefix}_HTTP_TIMEOUT_MS={int(v_env * 1000)}")
            else:
                env_lines.append(f"{_env_name(prefix, key)}={_env_value(v_env)}")
            effective = v_env
        # A trap on this key, independent of where its value really comes from.
        trap = rng.choice(TRAPS)
        decoy = _value(rng, key)
        if trap == "eu_overlay":
            _set(overlays["prod-eu"], key, decoy)
        elif trap == "commented_env":
            env_lines.append(f"# {_env_name(prefix, key)}={_env_value(decoy)}   # tried during INC-{rng.randint(1000, 2999)}")
        elif trap == "deprecated_block":
            _set(deprecated, key, decoy)
        elif trap == "foreign_prefix":
            env_lines.append(f"LEGACY{rng.randint(1, 9)}_{key.replace('.', '_').upper()}={_env_value(decoy)}")
        elif trap == "ms_env" and key == "http.timeout_s" and source != "env":
            # A millisecond variable under a foreign prefix: wrong unit AND wrong owner.
            env_lines.append(f"OPS_HTTP_TIMEOUT_MS={int(decoy * 1000)}")
        truth[key] = effective
        _set(overlays["staging"], key, _value(rng, key))
    rng.shuffle(env_lines)
    if deprecated:
        base["deprecated"] = deprecated
    files = {
        "config/base.yaml": "\n".join(_yaml(base)) + "\n",
        "deploy/prod.env": "\n".join(env_lines) + "\n",
    }
    for dep, tree in overlays.items():
        files[f"config/overlays/{dep}.yaml"] = ("\n".join(_yaml(tree)) if tree else "# no overrides") + "\n"
    truth["violations"] = sorted(k for k, (op, lim) in LIMITS.items()
                                 if (truth[k] > lim if op == "<=" else truth[k] < lim))
    return files, truth


def generate(seed, out=None, n=N_SERVICES):
    rng = rng_for(seed, "plan")
    words = ["checkout", "catalog", "search", "billing", "ledger", "pricing", "profile", "gateway",
             "inventory", "orders", "fulfil", "returns", "reviews", "media", "notify", "session",
             "tax", "fraud", "loyalty", "promo", "shipping", "tracking", "wallet", "payout",
             "export", "import", "reports", "audit", "consent", "identity", "support", "chat",
             "maps", "quotes", "rates", "stock"]
    pool = [f"{w}-{kind}" for w in words for kind in ("svc", "api", "worker")]
    names = rng.sample(pool, n)
    truth = {"seed": seed, "services": {}}
    for name in names:
        files, t = build_service(rng_for(seed, "svc", name), name)
        truth["services"][name] = {**t, "unit_chars": sum(len(v) for v in files.values())}
        if out is not None:
            for rel, text in files.items():
                write(Path(out) / "workspace" / "services" / name, rel, text)
    if out is not None:
        write(Path(out) / "workspace", "docs/CONFIG.md", CONFIG_MD)
        write(Path(out) / "workspace", "docs/SLO_LIMITS.md", SLO_MD)
    return truth


def _same(a, b):
    if isinstance(b, bool) or isinstance(a, bool):
        return a is b
    try:
        return abs(float(a) - float(b)) < 1e-6
    except (TypeError, ValueError):
        return False


def grade(seed, answer):
    """Per service, five items: the four effective values and the violations set.
    Reward is the mean over services of the fraction of items right."""
    truth = generate(seed)
    per = {}
    for name, t in truth["services"].items():
        got = answer.get(name) if isinstance(answer, dict) else None
        if not isinstance(got, dict):
            per[name] = 0.0
            continue
        items = [_same(got.get(k), t[k]) for k in KEYS]
        items.append(sorted(got.get("violations") or []) == t["violations"])
        per[name] = sum(items) / len(items)
    return {"reward": round(sum(per.values()) / len(per), 4), "services": per}


def oracle(seed):
    return {n: {**{k: t[k] for k in KEYS}, "violations": t["violations"]}
            for n, t in generate(seed)["services"].items()}


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [s["unit_chars"] for s in t["services"].values()],
            "judgement_turns": 4, "orchestration_turns": 12,
            "shared_chars": len(CONFIG_MD) + len(SLO_MD)}


ANSWER_PATH = "/workspace/answer/effective.json"
INSTRUCTION = """\
# Effective production config audit

Before the capacity review we need to know what every service under
`/workspace/services/` actually runs with in **prod**. Read `docs/CONFIG.md`
for how configuration resolves, and `docs/SLO_LIMITS.md` for the limits.

For each service, give the effective prod value of `db.pool_size`,
`http.timeout_s` (seconds), `feature.new_checkout` and `cache.ttl_s`, and list
which of those settings break a limit.

Write `/workspace/answer/effective.json`:

```json
{
  "<service>": {"db.pool_size": 20, "http.timeout_s": 12.5, "feature.new_checkout": true,
                "cache.ttl_s": 300, "violations": ["db.pool_size"]}
}
```

A service left out counts as wrong. Do not change any configuration.
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
        print(json.dumps(grade(args.seed, answer if isinstance(answer, dict) else {}), indent=2))
    elif args.solve:
        write(Path(args.solve).parent, Path(args.solve).name, json.dumps(oracle(args.seed), indent=2))
    else:
        generate(args.seed, args.out)


if __name__ == "__main__":
    main()
