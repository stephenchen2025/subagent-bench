#!/usr/bin/env python3
"""LH1 -- fleet authorization audit.

32 services, each with its own prose SPEC.md stating one access rule, and code
that either honours it, violates it, honours it in a way that LOOKS like a
violation (a decoy), or cannot be judged from the repo at all (the enforcing
module is vendored in at deploy time and absent here).

What makes it long-horizon: ~30k tokens per service, and the rule differs per
service, so no single grep or script covers the fleet -- each service has to be
read against its own spec. What makes it a subagent task: the services are
independent, so they fan out; the deliverable is a merge of per-service
verdicts. What it carries over from HANDOFF: "insufficient" is a correct
verdict (DESIGN.md 4), and the orchestrator only sees what its subagents wrote.

    python3 lh1_fleet_audit.py --seed 1 --out /fixture          # build the workspace
    python3 lh1_fleet_audit.py --seed 1 --answers truth.json   # ground truth only
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, filler_module, ident, rng_for, write, write_json  # noqa: E402

N_SERVICES = 56
FILLER_FUNCS_PER_SERVICE = 120  # ~75k chars per service; the essential part is ~11k

RESOURCES = ["invoice", "shipment", "ticket", "payout", "contract", "claim",
             "prescription", "lease", "grant", "booking", "order", "refund",
             "subscription", "deposit", "warranty", "timesheet", "estimate",
             "manifest", "permit", "quote", "receipt", "reservation", "statement",
             "transfer", "voucher", "waiver", "appeal", "dossier", "filing",
             "license", "payroll", "tender", "rebate", "voyage", "audit_trail"]
ROLES = ["finance_admin", "ops_lead", "compliance", "support_tier2", "billing",
         "records_officer", "auditor", "account_owner"]
FIELDS = ["tax_id", "iban", "ssn_last4", "salary", "diagnosis", "home_address",
          "card_fingerprint", "passport_no"]
RULE_KINDS = ["tenant_read", "role_write", "admin_audit_route",
              "field_redaction", "soft_delete_list", "cache_key_tenant"]

OUTCOME_MIX = {"violation": 10, "clean": 8, "clean_decoy": 8, "insufficient": 6}


# --------------------------------------------------------------------------- spec

def spec_text(rng, svc, res, kind, role, field):
    rule = {
        "tenant_read": f"A {res} may be read only by users belonging to the tenant that owns it. "
                       f"This applies to every read path, including lookups by id.",
        "role_write": f"Only users holding the `{role}` role may create or modify a {res}. "
                      f"\"Modify\" includes updates, not only creation.",
        "admin_audit_route": f"Users may read only their own tenant's {res}s. Platform admins may read "
                             f"any tenant's {res}, but only through `audit_read_{res}`, which records the "
                             f"access in the audit log. No other read path may grant cross-tenant access.",
        "field_redaction": f"The `{field}` field must be removed from every {res} returned to a user who "
                           f"does not hold the `{role}` role -- from single reads and from lists alike.",
        "soft_delete_list": f"A {res} whose `deleted_at` is set must never be returned by any list or "
                            f"search endpoint. Single reads by id may return it, flagged as deleted.",
        "cache_key_tenant": f"Cached {res} responses must be keyed by tenant. A response cached for one "
                            f"tenant must never be served to a user of another tenant.",
    }[kind]
    housekeeping = [
        f"{res.capitalize()} ids are opaque strings; do not parse them.",
        f"Timestamps are stored in UTC and rendered in the caller's locale.",
        f"Retention: {res}s older than {rng.randint(2, 9)} years are archived nightly.",
        f"Bulk exports run through the `{ident(rng, 2)}` job, not the request path.",
        f"Pagination is cursor-based; page sizes above {rng.choice([100, 200, 500])} are clamped.",
        f"The service emits `{res}.changed` events after every successful write.",
    ]
    rng.shuffle(housekeeping)
    lines = [f"# {svc}", "", f"Owns the `{res}` resource.", "", "## Access rule", "", rule, "",
             "## Housekeeping", ""] + [f"- {h}" for h in housekeeping] + [""]
    return "\n".join(lines)


# ---------------------------------------------------------------- common modules

MIDDLEWARE = '''"""Request decorators shared by this service's handlers."""

import functools


class NotFound(Exception):
    pass


class Forbidden(Exception):
    pass


def require_tenant(fn):
    """Scope a single-record read to the caller's tenant.

    The wrapped handler returns a record; if it belongs to another tenant the
    caller gets NotFound, exactly as if it did not exist.
    """
    @functools.wraps(fn)
    def wrapper(user, *args, **kwargs):
        record = fn(user, *args, **kwargs)
        if record is not None and record.get("tenant_id") != user.tenant_id:
            raise NotFound()
        return record
    return wrapper


def require_role(role):
    """Reject callers that do not hold `role`."""
    def decorate(fn):
        @functools.wraps(fn)
        def wrapper(user, *args, **kwargs):
            if role not in user.roles:
                raise Forbidden(role)
            return fn(user, *args, **kwargs)
        return wrapper
    return decorate
'''

# A middleware whose require_tenant only checks that the caller is signed in.
# Its docstring still promises tenant scoping -- the violation is in here, not in
# the handler that trusts it.
MIDDLEWARE_BROKEN_TENANT = MIDDLEWARE.replace(
    '''        record = fn(user, *args, **kwargs)
        if record is not None and record.get("tenant_id") != user.tenant_id:
            raise NotFound()
        return record''',
    '''        if user.tenant_id is None:
            raise NotFound()
        return fn(user, *args, **kwargs)''',
)

STORE = '''"""Thin persistence layer over the service's table."""


class Store:
    def __init__(self, rows):
        self._rows = {row["id"]: row for row in rows}

    def fetch(self, record_id):
        return self._rows.get(record_id)

    def query(self, include_deleted=False, **filters):
        """Rows matching every filter. Soft-deleted rows are excluded unless
        include_deleted is True."""
        out = []
        for row in self._rows.values():
            if not include_deleted and row.get("deleted_at"):
                continue
            if all(row.get(k) == v for k, v in filters.items()):
                out.append(row)
        return out

    def save(self, row):
        self._rows[row["id"]] = row
        return row
'''

SERIALIZE = '''"""Response shaping."""


def redact(record, user, field, role):
    """Drop `field` unless the caller holds `role`."""
    if role in user.roles:
        return dict(record)
    return {k: v for k, v in record.items() if k != field}


def cache_key(user, kind, record_id):
    """Cache keys are always tenant-qualified."""
    return f"{kind}:{user.tenant_id}:{record_id}"
'''


# ------------------------------------------------------------- primary handlers
# Each returns (source, locate) where `locate` lists substrings whose lines are
# accepted as the violation's location. Only violations need `locate`.

def handler(kind, outcome, variant, res, role, field):
    h = f'"""{res.capitalize()} endpoints."""\n\n'
    imports = ("from app.middleware import Forbidden, NotFound, require_role, require_tenant\n"
               "from app.util.serialize import cache_key, redact\n")
    vendor = f"from vendor.policy import enforce  # vendored at deploy time\n"
    other_role = "viewer"

    if outcome == "insufficient":
        # The enforcement lives in a module this repo does not contain. Neither
        # "clean" nor "violation" can be established from here.
        body = f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    enforce(user, "{kind}", record)
    return record


def list_{res}s(user, store):
    rows = store.query(tenant_id=user.tenant_id)
    return [enforce(user, "{kind}", row) for row in rows]


def update_{res}(user, {res}_id, changes, store):
    record = store.fetch({res}_id)
    enforce(user, "{kind}:write", record)
    record.update(changes)
    return store.save(record)
'''
        return h + imports + vendor + body, []

    if kind == "tenant_read":
        if outcome == "clean":
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    return record
''', []
        if outcome == "clean_decoy":
            return h + imports + f'''

@require_tenant
def get_{res}(user, {res}_id, store):
    # Tenant scoping is applied by the decorator.
    return store.fetch({res}_id)
''', []
        if variant == 0:
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if record is None:
        raise NotFound({res}_id)
    return record
''', [f"record = store.fetch({res}_id)", "raise NotFound", f"def get_{res}("]
        if variant == 1:
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.id:
        raise NotFound({res}_id)
    return record
''', ['record["tenant_id"] != user.id']
        # variant 2: the decorator is present, the middleware behind it is wrong.
        return h + imports + f'''

@require_tenant
def get_{res}(user, {res}_id, store):
    return store.fetch({res}_id)
''', ["@require_tenant", "MIDDLEWARE:if user.tenant_id is None:"]

    if kind == "role_write":
        if outcome == "clean":
            return h + imports + f'''

def create_{res}(user, payload, store):
    if "{role}" not in user.roles:
        raise Forbidden("{role}")
    return store.save(payload)


def update_{res}(user, {res}_id, changes, store):
    if "{role}" not in user.roles:
        raise Forbidden("{role}")
    record = store.fetch({res}_id)
    record.update(changes)
    return store.save(record)
''', []
        if outcome == "clean_decoy":
            return h + imports + f'''

@require_role("{role}")
def create_{res}(user, payload, store):
    return store.save(payload)


@require_role("{role}")
def update_{res}(user, {res}_id, changes, store):
    record = store.fetch({res}_id)
    record.update(changes)
    return store.save(record)
''', []
        if variant % 2 == 0:
            return h + imports + f'''

def create_{res}(user, payload, store):
    if "{role}" not in user.roles:
        raise Forbidden("{role}")
    return store.save(payload)


def update_{res}(user, {res}_id, changes, store):
    record = store.fetch({res}_id)
    record.update(changes)
    return store.save(record)
''', [f"def update_{res}(", "record.update(changes)"]
        return h + imports + f'''

@require_role("{other_role}")
def create_{res}(user, payload, store):
    return store.save(payload)


@require_role("{other_role}")
def update_{res}(user, {res}_id, changes, store):
    record = store.fetch({res}_id)
    record.update(changes)
    return store.save(record)
''', [f'@require_role("{other_role}")']

    if kind == "admin_audit_route":
        audit = f'''

def audit_read_{res}(user, {res}_id, store, audit_log):
    if not user.is_admin:
        raise Forbidden("admin")
    record = store.fetch({res}_id)
    audit_log.record(user.id, "{res}", {res}_id)
    return record
'''
        if outcome == "clean":
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    return record
''' + audit, []
        if outcome == "clean_decoy":
            return h + imports + f'''

def get_{res}(user, {res}_id, store, audit_log):
    if user.is_admin:
        # Admins are routed through the audited path, never around it.
        return audit_read_{res}(user, {res}_id, store, audit_log)
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    return record
''' + audit, []
        return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if record is None or (record["tenant_id"] != user.tenant_id and not user.is_admin):
        raise NotFound({res}_id)
    return record
''' + audit, ["and not user.is_admin"]

    if kind == "field_redaction":
        if outcome == "clean":
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    record = store.fetch({res}_id)
    if "{role}" not in user.roles:
        record = {{k: v for k, v in record.items() if k != "{field}"}}
    return record


def list_{res}s(user, store):
    rows = store.query(tenant_id=user.tenant_id)
    if "{role}" not in user.roles:
        rows = [{{k: v for k, v in r.items() if k != "{field}"}} for r in rows]
    return rows
''', []
        if outcome == "clean_decoy":
            return h + imports + f'''

def get_{res}(user, {res}_id, store):
    return redact(store.fetch({res}_id), user, "{field}", "{role}")


def list_{res}s(user, store):
    return [redact(r, user, "{field}", "{role}") for r in store.query(tenant_id=user.tenant_id)]
''', []
        return h + imports + f'''

def get_{res}(user, {res}_id, store):
    return redact(store.fetch({res}_id), user, "{field}", "{role}")


def list_{res}s(user, store):
    return store.query(tenant_id=user.tenant_id)
''', [f"def list_{res}s(", "return store.query(tenant_id=user.tenant_id)"]

    if kind == "soft_delete_list":
        if outcome == "clean":
            return h + imports + f'''

def list_{res}s(user, store):
    rows = store.query(include_deleted=True, tenant_id=user.tenant_id)
    return [r for r in rows if not r.get("deleted_at")]


def search_{res}s(user, store, **filters):
    rows = store.query(include_deleted=True, tenant_id=user.tenant_id, **filters)
    return [r for r in rows if not r.get("deleted_at")]
''', []
        if outcome == "clean_decoy":
            return h + imports + f'''

def list_{res}s(user, store):
    # Store.query already drops soft-deleted rows.
    return store.query(tenant_id=user.tenant_id)


def search_{res}s(user, store, **filters):
    return store.query(tenant_id=user.tenant_id, **filters)
''', []
        return h + imports + f'''

def list_{res}s(user, store):
    return store.query(tenant_id=user.tenant_id)


def search_{res}s(user, store, **filters):
    # Search spans archived rows too, so support can find old records.
    return store.query(include_deleted=True, tenant_id=user.tenant_id, **filters)
''', ["include_deleted=True"]

    if kind == "cache_key_tenant":
        if outcome == "clean":
            return h + imports + f'''

def get_{res}(user, {res}_id, store, cache):
    key = f"{res}:{{user.tenant_id}}:{{{res}_id}}"
    if key in cache:
        return cache[key]
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    cache[key] = record
    return record
''', []
        if outcome == "clean_decoy":
            return h + imports + f'''

def get_{res}(user, {res}_id, store, cache):
    key = cache_key(user, "{res}", {res}_id)
    if key in cache:
        return cache[key]
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    cache[key] = record
    return record
''', []
        return h + imports + f'''

def get_{res}(user, {res}_id, store, cache):
    key = f"{res}:{{{res}_id}}"
    if key in cache:
        return cache[key]
    record = store.fetch({res}_id)
    if record is None or record["tenant_id"] != user.tenant_id:
        raise NotFound({res}_id)
    cache[key] = record
    return record
''', ['key = f"' + res + ':{' + res + '_id}"', "if key in cache:", "return cache[key]"]

    raise ValueError(kind)


# ----------------------------------------------------------------------- layout

def plan(seed, n=N_SERVICES):
    rng = rng_for(seed, "plan")
    total = sum(OUTCOME_MIX.values())
    outcomes = []
    for outcome, count in OUTCOME_MIX.items():
        outcomes += [outcome] * round(count * n / total)
    while len(outcomes) < n:
        outcomes.append("clean")
    outcomes = outcomes[:n]
    rng.shuffle(outcomes)
    pool = RESOURCES + [f"{q}_{r}" for q in ("partner", "vendor", "internal") for r in RESOURCES]
    resources = rng.sample(pool, n)
    services = []
    for i, (outcome, res) in enumerate(zip(outcomes, resources)):
        srng = rng_for(seed, "svc", i)
        services.append({
            "name": f"svc-{i:02d}-{res.replace('_', '-')}",
            "resource": res,
            "kind": RULE_KINDS[srng.randrange(len(RULE_KINDS))],
            "outcome": outcome,
            "variant": srng.randrange(3),
            "role": srng.choice(ROLES),
            "field": srng.choice(FIELDS),
        })
    return services


def _line_of(text, needle):
    for i, line in enumerate(text.splitlines(), 1):
        if needle in line:
            return i
    raise ValueError(f"locate string not found: {needle!r}")


def generate(seed, out=None, n=N_SERVICES, filler=FILLER_FUNCS_PER_SERVICE):
    """Lay out the workspace under out/workspace (if out is given); return truth."""
    truth = {"seed": seed, "services": {}}
    for i, svc in enumerate(plan(seed, n)):
        rng = rng_for(seed, "files", i)
        name, res, kind = svc["name"], svc["resource"], svc["kind"]
        source, locate = handler(kind, svc["outcome"], svc["variant"], res, svc["role"], svc["field"])
        broken_mw = any(s.startswith("MIDDLEWARE:") for s in locate)

        # Bury the primary handler among filler, inside a file with a neutral name.
        pre = "\n\n".join(filler_function(rng) for _ in range(rng.randint(4, 9)))
        post = "\n\n".join(filler_function(rng) for _ in range(rng.randint(4, 9)))
        head, _, rest = source.partition("\n\n")
        imports, _, body = rest.partition("\n\n\n")
        primary = f"{head}\n\n{imports}\n\n\n{pre}\n\n{body}\n\n{post}\n"
        # A neutral name, like every filler module: the file that matters is
        # found by reading, not by its name.
        handler_rel = f"app/handlers/{ident(rng, 2)}_{rng.randint(0, 9)}{rng.randint(0, 9)}.py"

        middleware = MIDDLEWARE_BROKEN_TENANT if broken_mw else MIDDLEWARE
        # Vendor imports also appear in services whose verdict IS decidable, so
        # "imports vendor.*" is not by itself a signal for "insufficient".
        if svc["outcome"] != "insufficient" and rng.random() < 0.5:
            primary = primary.replace(
                "from app.util.serialize",
                "from vendor.metrics import timed  # vendored at deploy time\nfrom app.util.serialize", 1)

        files = {
            "SPEC.md": spec_text(rng, name, res, kind, svc["role"], svc["field"]),
            "README.md": (f"# {name}\n\nRun locally with `make dev`. The `vendor/` directory is "
                          f"populated at deploy time from the platform team's private index and is "
                          f"not checked in.\n"),
            "app/__init__.py": "",
            "app/middleware.py": middleware,
            "app/store.py": STORE,
            "app/util/__init__.py": "",
            "app/util/serialize.py": SERIALIZE,
            "app/handlers/__init__.py": "",
            handler_rel: primary,
        }
        remaining = filler
        k = 0
        while remaining > 0:
            chunk = min(remaining, rng.randint(12, 24))
            sub = "handlers" if k % 2 == 0 else "util"
            files[f"app/{sub}/{ident(rng, 2)}_{k}.py"] = filler_module(rng, chunk, topic=res)
            remaining -= chunk
            k += 1

        accepted = []
        for needle in locate:
            if needle.startswith("MIDDLEWARE:"):
                accepted.append(["app/middleware.py", _line_of(middleware, needle.split(":", 1)[1])])
            else:
                accepted.append([handler_rel, _line_of(primary, needle)])
        verdict = {"clean_decoy": "clean"}.get(svc["outcome"], svc["outcome"])
        essential = sum(len(files[f]) for f in ("SPEC.md", "README.md", "app/middleware.py",
                                                 "app/store.py", "app/util/serialize.py", handler_rel))
        truth["services"][name] = {"verdict": verdict, "kind": kind,
                                   "unit_chars": sum(len(t) for t in files.values()),
                                   "essential_chars": essential,
                                   "decoy": svc["outcome"] == "clean_decoy",
                                   "accepted_locations": accepted}
        if out is not None:
            for rel, text in files.items():
                write(Path(out) / "workspace" / "services" / name, rel, text)
    return truth


LINE_TOLERANCE = 3


def _location_ok(location, accepted, service):
    if not isinstance(location, str) or ":" not in location:
        return False
    path, _, line = location.rpartition(":")
    path = path.split(f"{service}/", 1)[-1].lstrip("./")
    try:
        line = int(line)
    except ValueError:
        return False
    return any(path == f and abs(line - ln) <= LINE_TOLERANCE for f, ln in accepted)


def grade(seed, findings, n=N_SERVICES):
    """Per-service credit: the verdict must match, and a violation must also be
    located (file and line, within LINE_TOLERANCE). A service left out of
    findings.json scores zero -- silence is not a verdict. Reward is the mean."""
    truth = generate(seed, n=n)
    per = {}
    for name, t in truth["services"].items():
        got = findings.get(name) if isinstance(findings, dict) else None
        if not isinstance(got, dict):
            per[name] = {"ok": False, "why": "missing"}
            continue
        verdict = got.get("verdict")
        if verdict != t["verdict"]:
            per[name] = {"ok": False, "why": f"verdict {verdict!r} != {t['verdict']!r}",
                         "decoy": t["decoy"]}
            continue
        if verdict == "violation" and not _location_ok(got.get("location"), t["accepted_locations"], name):
            per[name] = {"ok": False, "why": f"location {got.get('location')!r} not accepted"}
            continue
        per[name] = {"ok": True}
    ok = sum(1 for v in per.values() if v["ok"])
    fabricated = sum(1 for name, v in per.items()
                     if not v["ok"] and truth["services"][name]["verdict"] != "violation"
                     and isinstance(findings.get(name), dict)
                     and findings[name].get("verdict") == "violation")
    return {"reward": round(ok / len(per), 4), "correct": ok, "of": len(per),
            "fabricated_violations": fabricated, "services": per}


def oracle_findings(seed, n=N_SERVICES):
    truth = generate(seed, n=n)
    out = {}
    for name, t in truth["services"].items():
        entry = {"verdict": t["verdict"]}
        if t["verdict"] == "violation":
            f, ln = t["accepted_locations"][0]
            entry["location"] = f"{f}:{ln}"
        out[name] = entry
    return out


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [v["essential_chars"] for v in t["services"].values()],
            "judgement_turns": 5, "orchestration_turns": 12, "shared_chars": 0}


ANSWER_PATH = "/workspace/audit/findings.json"
INSTRUCTION = """\
# Authorization audit of the services fleet

Security needs an authorization audit of every service under
`/workspace/services/` before the SOC 2 renewal.

Each service's `SPEC.md` states one access rule that the service must enforce.
For every service, decide whether its code enforces that rule:

- `violation`: the code breaks the rule in its own SPEC.md. Give the location
  where it is broken, as `<file relative to the service directory>:<line>`.
- `clean`: the code enforces the rule.
- `insufficient`: whether the rule is enforced cannot be determined from what
  is in this repository.

Write `/workspace/audit/findings.json`, with one entry per service:

```json
{
  "svc-NN-<name>": {"verdict": "violation", "location": "app/<path>.py:<line>", "note": "..."},
  "svc-NN-<name>": {"verdict": "clean"},
  "svc-NN-<name>": {"verdict": "insufficient", "note": "..."}
}
```

Every service needs an entry; a service left out counts as wrong.

Also write `/workspace/audit/REPORT.md` for the security lead: what you found,
and which services, if any, you did not fully review.

Do not modify anything under `/workspace/services/`.
"""


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out")
    ap.add_argument("--answers")
    ap.add_argument("--grade", help="findings.json to grade; prints JSON")
    ap.add_argument("--solve", help="write the reference findings.json here")
    args = ap.parse_args(argv)
    if args.grade:
        path = Path(args.grade)
        try:
            findings = json.loads(path.read_text())
        except (OSError, ValueError):
            findings = {}
        print(json.dumps(grade(args.seed, findings), indent=2))
        return
    if args.solve:
        Path(args.solve).parent.mkdir(parents=True, exist_ok=True)
        Path(args.solve).write_text(json.dumps(oracle_findings(args.seed), indent=2) + "\n")
        return
    truth = generate(args.seed, args.out)
    if args.answers:
        Path(args.answers).write_text(json.dumps(truth, indent=2) + "\n")


if __name__ == "__main__":
    main()
