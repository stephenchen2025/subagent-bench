#!/usr/bin/env python3
"""LH10 -- which of 64 columns proposed for deletion are safe to drop?

The DBA proposal (proposals/drop_columns.md) lists 64 `table.column` pairs. For
each, the brief asks: is anything in production still reading or writing it?
docs/DROP_POLICY.md defines "production": code under app/, the settings it
reads, and the external consumers registered in db/external_consumers.yaml --
not tests, not migrations, not comments.

The codebase is shared, so the units are the columns, not the files. Every
column needs a whole-repo search whose hits must each be judged:

- **name collisions** -- `status` exists on several tables; `Invoice.status`
  is not a use of `orders.status`;
- **dead mentions** -- comments, tests and migrations mention columns that
  nothing reads;
- **indirect reads** -- a generic exporter does `getattr(row, f)` over a field
  list in app/settings.py (resolvable: unsafe), or over a list read from an
  environment variable at runtime (unresolvable: `insufficient`);
- **external readers** -- another team's ETL, registered in a YAML file.

    python3 lh10_column_drop.py --seed 1 --out /fixture
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, rng_for, write  # noqa: E402

N_COLUMNS = 64
TABLES = ["orders", "invoices", "customers", "shipments", "payments", "refunds", "products",
          "carts", "coupons", "reviews", "tickets", "accounts", "sessions", "addresses",
          "subscriptions", "warehouses"]
SHARED_NAMES = ["status", "notes", "source", "region", "legacy_flag", "created_by", "updated_by",
                "external_ref", "priority", "channel"]
OWN_NAMES = ["fx_rate_v1", "old_sku", "promo_code_raw", "risk_score_v0", "carrier_hint",
             "sync_token", "import_batch", "display_name_old", "tax_code_legacy", "tier_v1",
             "geo_hash", "referrer_raw", "checksum_md5", "archived_reason", "manual_override"]
SCENARIOS = {  # name: (verdict, count per 64)
    "safe_unused": ("safe", 8),
    "safe_name_collision": ("safe", 8),
    "safe_comment_test_migration": ("safe", 8),
    "unsafe_orm": ("unsafe", 9),
    "unsafe_raw_sql": ("unsafe", 8),
    "unsafe_settings_dynamic": ("unsafe", 7),
    "unsafe_external": ("unsafe", 7),
    "insufficient_env_dynamic": ("insufficient", 9),
}

POLICY = """# Column drop policy

A column may be dropped only when nothing in production reads or writes it.

"Production" means:

- code under `app/` that reads or writes the column (not `tests/`, not
  `db/migrations/`, not comments -- and declaring the column on its model in
  `app/models.py` is not a use);
- field lists in `app/settings.py`, which the generic exporter reads;
- other teams' pipelines registered in `db/external_consumers.yaml`.

If whether a column is read depends on something that is not in this
repository (for example a field list read from the environment at runtime),
the column cannot be cleared.
"""


def model_name(table):
    return "".join(w.capitalize() for w in (table[:-1] if table.endswith("s") else table).split("_"))


def plan(seed, n=N_COLUMNS):
    rng = rng_for(seed, "plan")
    schema = {}
    for t in TABLES:
        cols = ["id", "created_at"] + rng.sample(SHARED_NAMES, 5) + rng.sample(OWN_NAMES, 3)
        schema[t] = list(dict.fromkeys(cols))
    kinds = []
    for kind, (_, count) in SCENARIOS.items():
        kinds += [kind] * round(count * n / 64)
    kinds = (kinds + ["safe_unused"] * n)[:n]
    rng.shuffle(kinds)
    pool = [(t, c) for t in TABLES for c in schema[t] if c not in ("id", "created_at")]
    rng.shuffle(pool)
    shared_pool = [(t, c) for t, c in pool if c in SHARED_NAMES]
    candidates, used = [], set()
    for kind in kinds:
        source = shared_pool if kind == "safe_name_collision" else pool
        t, c = next((t, c) for t, c in source if (t, c) not in used)
        used.add((t, c))
        candidates.append({"table": t, "column": c, "kind": kind})
    return schema, candidates


def generate(seed, out=None, n=N_COLUMNS):
    rng = rng_for(seed, "code")
    schema, candidates = plan(seed, n)
    cand_set = {(c["table"], c["column"]) for c in candidates}
    n_modules = 28
    modules = {i: [filler_function(rng) for _ in range(rng.randint(14, 22))] for i in range(n_modules)}
    plants = {}  # (table, column) -> list of (relpath, needle)
    settings_fields, external, env_lines, tests, migrations = {}, [], [], [], []

    def plant(mod_i, snippet, key, needle):
        modules[mod_i].insert(rng.randint(0, len(modules[mod_i])), snippet)
        if key is not None:
            plants.setdefault(key, []).append((f"app/services/svc_{mod_i:02d}.py", needle))

    for c in candidates:
        t, col, kind = c["table"], c["column"], c["kind"]
        m = model_name(t)
        fn = f"{rng.choice(['summarize', 'export', 'reconcile', 'render'])}_{t}_{col}"
        if kind == "unsafe_orm":
            needle = f"row.{col}"
            plant(rng.randrange(n_modules),
                  f"def {fn}():\n    from app.models import {m}\n    out = []\n"
                  f"    for row in {m}.query().all():\n        out.append({needle})\n    return out\n",
                  (t, col), needle)
        elif kind == "unsafe_raw_sql":
            needle = f"SELECT id, {col} FROM {t}"
            plant(rng.randrange(n_modules),
                  f"def {fn}(cur):\n    cur.execute(\"{needle} WHERE created_at > now() - interval '1 day'\")\n"
                  f"    return cur.fetchall()\n", (t, col), needle)
        elif kind == "unsafe_settings_dynamic":
            settings_fields.setdefault(t, ["id"]).append(col)
        elif kind == "unsafe_external":
            external.append((t, col))
        elif kind == "insufficient_env_dynamic":
            var = f"{t.upper()}_AUDIT_FIELDS"
            env_lines.append((t, var))
            plant(rng.randrange(n_modules),
                  f"def audit_{t}_{rng.randint(10, 99)}():\n    import os\n    from app.models import {m}\n"
                  f"    fields = os.environ.get(\"{var}\", \"id\").split(\",\")\n"
                  f"    return [[getattr(row, f) for f in fields] for row in {m}.query().all()]\n", None, None)
        elif kind == "safe_name_collision":
            other = next((o for o in TABLES if o != t and col in schema[o] and (o, col) not in cand_set), None)
            if other is None:
                # Never let a decoy read another CANDIDATE: give the name to a
                # table that does not have it yet, as a non-candidate column.
                other = next(o for o in TABLES if o != t and col not in schema[o])
                schema[other].append(col)
            om = model_name(other)
            plant(rng.randrange(n_modules),
                  f"def {fn}():\n    from app.models import {om}\n"
                  f"    return [row.{col} for row in {om}.query().all()]\n", None, None)
            plant(rng.randrange(n_modules),
                  f"def {fn}_sql(cur):\n    cur.execute(\"SELECT id, {col} FROM {other}\")\n"
                  f"    return cur.fetchall()\n", None, None)
        elif kind == "safe_comment_test_migration":
            plant(rng.randrange(n_modules),
                  f"def {fn}():\n    # {t}.{col} used to be read here; removed in the 2025 cleanup.\n"
                  f"    return None\n", None, None)
        # Every candidate also shows up in tests and migrations -- noise either way.
        tests.append(f"def test_{t}_{col}_roundtrip():\n    from app.models import {m}\n"
                     f"    assert hasattr({m}, \"{col}\")\n")
        migrations.append(f"-- add {t}.{col}\nALTER TABLE {t} ADD COLUMN {col} TEXT;\n")

    files = {}
    for i, funcs in modules.items():
        files[f"app/services/svc_{i:02d}.py"] = f'"""Service module {i:02d}."""\n\n\n' + "\n\n".join(funcs)
    # Settings and external readers are unsafe via config, not code.
    settings_lines = ['"""Settings read by app.services.exporter."""', "", "EXPORT_FIELDS = {"]
    for t, fields in sorted(settings_fields.items()):
        settings_lines.append(f'    "{t}": {fields!r},')
    settings_lines.append("}")
    files["app/settings.py"] = "\n".join(settings_lines) + "\n"
    files["app/services/exporter.py"] = ('"""Generic exporter: reads the fields listed in settings."""\n\n'
                                         "from app import models, settings\n\n\n"
                                         "def export(table):\n"
                                         "    model = models.for_table(table)\n"
                                         "    fields = settings.EXPORT_FIELDS[table]\n"
                                         "    return [[getattr(row, f) for f in fields] for row in model.query().all()]\n")
    for t, fields in settings_fields.items():
        for col in fields[1:]:
            plants.setdefault((t, col), []).append(("app/settings.py", f'"{t}":'))
    ext = ["# Other teams' pipelines that read our tables directly.", "consumers:"]
    for t, col in external:
        team = rng.choice(["finance-etl", "growth-analytics", "risk-models", "support-bi"])
        ext += [f"  - team: {team}", f"    reads: {t}.{col}"]
        plants.setdefault((t, col), []).append(("db/external_consumers.yaml", f"reads: {t}.{col}"))
    files["db/external_consumers.yaml"] = "\n".join(ext) + "\n"
    files["app/models.py"] = ('"""ORM models, one per table."""\n\n\nclass Model:\n    __table__ = None\n\n'
                              "    @classmethod\n    def query(cls):\n        raise NotImplementedError\n\n\n"
                              + "\n\n".join(f"class {model_name(t)}(Model):\n    __table__ = \"{t}\"\n"
                                            + "".join(f"    {c} = None\n" for c in cols)
                                            for t, cols in schema.items())
                              + "\n\n\ndef for_table(table):\n    return next(m for m in Model.__subclasses__() "
                                "if m.__table__ == table)\n")
    files["db/schema.sql"] = "\n\n".join(
        f"CREATE TABLE {t} (\n" + ",\n".join(f"    {c} {'BIGINT' if c == 'id' else 'TEXT'}" for c in cols) + "\n);"
        for t, cols in schema.items()) + "\n"
    files["tests/test_models.py"] = "\n\n".join(tests)
    for i, mig in enumerate(migrations):
        files[f"db/migrations/{i + 1:04d}_add_column.sql"] = mig
    files["docs/DROP_POLICY.md"] = POLICY
    files["proposals/drop_columns.md"] = ("# Columns proposed for deletion\n\n"
                                          + "\n".join(f"- `{c['table']}.{c['column']}`" for c in candidates) + "\n")

    truth = {"seed": seed, "columns": {}}
    for c in candidates:
        key = f"{c['table']}.{c['column']}"
        accepted = []
        for rel, needle in plants.get((c["table"], c["column"]), []):
            for i, line in enumerate(files[rel].splitlines(), 1):
                if needle in line:
                    accepted.append([rel, i])
        truth["columns"][key] = {"verdict": SCENARIOS[c["kind"]][0], "kind": c["kind"],
                                 "accepted_locations": accepted}
    repo_chars = sum(len(v) for v in files.values())
    truth["per_column_chars"] = 6000
    truth["repo_chars"] = repo_chars
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def _location_ok(loc, accepted):
    if not isinstance(loc, str) or ":" not in loc:
        return False
    path, _, line = loc.rpartition(":")
    path = path.lstrip("./").removeprefix("workspace/")
    try:
        line = int(line)
    except ValueError:
        return False
    return any(path == f and abs(line - ln) <= 3 for f, ln in accepted)


def grade(seed, answer):
    """Per column: the verdict must match; `unsafe` must also cite one real
    production use (file and line, within 3)."""
    truth = generate(seed)
    answer = answer if isinstance(answer, dict) else {}
    per = {}
    for key, t in truth["columns"].items():
        got = answer.get(key)
        ok = isinstance(got, dict) and got.get("verdict") == t["verdict"]
        if ok and t["verdict"] == "unsafe":
            ok = _location_ok(got.get("location"), t["accepted_locations"])
        per[key] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "columns": per}


def oracle(seed):
    out = {}
    for key, t in generate(seed)["columns"].items():
        entry = {"verdict": t["verdict"]}
        if t["verdict"] == "unsafe":
            f, ln = t["accepted_locations"][0]
            entry["location"] = f"{f}:{ln}"
        out[key] = entry
    return out


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [t["per_column_chars"]] * len(t["columns"]),
            "judgement_turns": 5, "orchestration_turns": 12, "shared_chars": len(POLICY) + 8000}


ANSWER_PATH = "/workspace/answer/columns.json"
INSTRUCTION = """\
# Which columns can we drop?

The DBA team wants to delete the columns in `proposals/drop_columns.md` to
reclaim space before the storage migration. `docs/DROP_POLICY.md` defines what
counts as a production use.

For every proposed column, decide:

- `safe`: nothing in production reads or writes it;
- `unsafe`: something does. Give one production location as `<path>:<line>`;
- `insufficient`: this cannot be determined from the repository.

Write `/workspace/answer/columns.json`:

```json
{"<table>.<column>": {"verdict": "unsafe", "location": "app/<path>:<line>"}}
```

A column left out counts as wrong. Do not modify the repository.
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
