#!/usr/bin/env python3
"""LH28 -- answer 240 access questions by evaluating IAM policies by hand.

iam/ holds 30 policy documents, 12 groups and 48 principals (some with a
permission boundary). questions/<principal>.md asks five questions per
principal: can they perform ACTION on RESOURCE from IP at TIME? The
evaluation rules are in docs/EVALUATION.md:

- gather the principal's own policies and every policy of every group they
  are in;
- an explicit Deny that matches wins over any Allow;
- otherwise any matching Allow allows -- but if the principal has a
  permission boundary, the boundary must ALSO allow it;
- Action patterns match case-insensitively with `*` and `?`; Resource
  patterns match case-sensitively;
- a statement matches only if all its conditions hold: source IP in a CIDR,
  a principal tag equal to a value, the time before a date.

Each principal is a separate evaluation over a different set of documents.

    python3 lh28_iam_access.py --seed 1 --out /fixture
"""

import fnmatch
import ipaddress
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_PRINCIPALS = 48
SERVICES = {"s3": ["GetObject", "PutObject", "DeleteObject", "ListBucket"],
            "dynamodb": ["GetItem", "PutItem", "Query", "DeleteTable"],
            "kms": ["Decrypt", "Encrypt", "ScheduleKeyDeletion"],
            "logs": ["GetLogEvents", "PutLogEvents", "DeleteLogGroup"]}
BUCKETS = ["reports", "invoices", "ml-data", "backups", "public-assets"]
TABLES = ["orders", "customers", "sessions"]
TEAMS = ["finance", "data", "platform", "growth"]


def resource(rng, svc):
    if svc == "s3":
        b = rng.choice(BUCKETS)
        return f"arn:aws:s3:::{b}/{rng.choice(['2026', 'archive', 'tmp'])}/{rng.choice(['q3.csv', 'x.parquet', 'Q3.CSV'])}"
    if svc == "dynamodb":
        return f"arn:aws:dynamodb:eu-west-1:111122223333:table/{rng.choice(TABLES)}"
    if svc == "kms":
        return f"arn:aws:kms:eu-west-1:111122223333:key/{rng.choice(['billing', 'data', 'shared'])}"
    return f"arn:aws:logs:eu-west-1:111122223333:log-group:/app/{rng.choice(['api', 'worker', 'audit'])}"


def pattern(rng, svc):
    action = rng.choice([f"{svc}:{rng.choice(SERVICES[svc])}", f"{svc}:Get*", f"{svc}:*", f"{svc}:Put*",
                         f"{svc.upper()}:{rng.choice(SERVICES[svc]).lower()}"])
    if svc == "s3":
        res = rng.choice([f"arn:aws:s3:::{rng.choice(BUCKETS)}/*", "arn:aws:s3:::*", f"arn:aws:s3:::{rng.choice(BUCKETS)}/2026/*",
                          f"arn:aws:s3:::{rng.choice(BUCKETS)}/2026/q3.csv", f"arn:aws:s3:::{rng.choice(BUCKETS)}/archive/q3.csv"])
    elif svc == "dynamodb":
        res = rng.choice([f"arn:aws:dynamodb:eu-west-1:111122223333:table/{rng.choice(TABLES)}",
                          "arn:aws:dynamodb:eu-west-1:111122223333:table/*"])
    elif svc == "kms":
        res = rng.choice(["arn:aws:kms:eu-west-1:111122223333:key/*", "arn:aws:kms:eu-west-1:111122223333:key/billing"])
    else:
        res = "arn:aws:logs:eu-west-1:111122223333:log-group:/app/*"
    return action, res


def recase(res):
    """Capitalise one name in a resource ARN (`reports` -> `Reports`): the same
    thing to a person, a different resource to IAM."""
    head, _, path = res.rpartition(":")
    parts = path.split("/")
    for i in range(len(parts) - 1, -1, -1):
        if parts[i][:1].islower():
            parts[i] = parts[i][:1].upper() + parts[i][1:]
            break
    return f"{head}:{'/'.join(parts)}"


def statement(rng, effect):
    svc = rng.choice(list(SERVICES))
    action, res = pattern(rng, svc)
    st = {"Effect": effect, "Action": [action], "Resource": [res]}
    roll = rng.random()
    if roll < 0.2:
        st["Condition"] = {"IpAddress": {"aws:SourceIp": rng.choice(["10.0.0.0/8", "192.168.10.0/24"])}}
    elif roll < 0.35:
        st["Condition"] = {"StringEquals": {"aws:PrincipalTag/team": rng.choice(TEAMS)}}
    elif roll < 0.45:
        st["Condition"] = {"DateLessThan": {"aws:CurrentTime": rng.choice(["2026-06-30T00:00:00Z", "2026-12-31T00:00:00Z"])}}
    return st


def cond_ok(cond, ctx):
    for op, kv in (cond or {}).items():
        for key, want in kv.items():
            if op == "IpAddress" and ipaddress.ip_address(ctx["ip"]) not in ipaddress.ip_network(want):
                return False
            if op == "StringEquals" and ctx["tags"].get(key.split("/", 1)[1]) != want:
                return False
            if op == "DateLessThan" and not ctx["time"] < want:
                return False
    return True


def matches(st, action, res, ctx):
    return (any(fnmatch.fnmatchcase(action.lower(), a.lower()) for a in st["Action"])
            and any(fnmatch.fnmatchcase(res, r) for r in st["Resource"]) and cond_ok(st.get("Condition"), ctx))


def evaluate(policies, boundary, action, res, ctx):
    stmts = [s for p in policies for s in p["Statement"]]
    if any(s["Effect"] == "Deny" and matches(s, action, res, ctx) for s in stmts):
        return "deny"
    if not any(s["Effect"] == "Allow" and matches(s, action, res, ctx) for s in stmts):
        return "deny"
    if boundary is not None and not any(s["Effect"] == "Allow" and matches(s, action, res, ctx)
                                        for s in boundary["Statement"]):
        return "deny"
    return "allow"


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    policies = {}
    for i in range(30):
        stmts = [statement(rng, "Allow") for _ in range(rng.randint(1, 4))]
        if rng.random() < 0.35:
            stmts.append(statement(rng, "Deny"))
        policies[f"pol-{i:02d}"] = {"Version": "2012-10-17", "Statement": stmts}
    groups = {f"grp-{g}": rng.sample(list(policies), rng.randint(1, 3)) for g in
              ["analysts", "admins", "oncall", "finance", "ml", "support", "readonly", "etl", "billing", "growth", "audit", "sre"]}
    # Boundaries are broad (whole services), so they cut some allows, not all.
    boundaries = {}
    for k in range(4):
        svcs = rng.sample(list(SERVICES), 2)
        boundaries[f"boundary-{k}"] = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow", "Action": [f"{svc}:*"], "Resource": ["*"]} for svc in svcs]}
    files = {"docs/EVALUATION.md": EVALUATION}
    for name, doc in {**policies, **boundaries}.items():
        files[f"iam/policies/{name}.json"] = json.dumps(doc, indent=2) + "\n"
    files["iam/groups.json"] = json.dumps(groups, indent=2) + "\n"
    principals, truth = {}, {"seed": seed, "principals": {}}
    people = ["alice", "bob", "chen", "dana", "eve", "farid", "gia", "hugo", "ines", "jon", "kai", "lea"]
    for i in range(N_PRINCIPALS):
        prng = rng_for(seed, "p", i)
        name = f"{prng.choice(people)}.{i:02d}"
        p = {"groups": prng.sample(list(groups), prng.randint(1, 2)), "policies": prng.sample(list(policies), prng.randint(0, 2)),
             "tags": {"team": prng.choice(TEAMS)}, "permission_boundary": prng.choice([None, None, None, None, *boundaries])}
        principals[name] = p
        docs = [policies[x] for x in p["policies"]] + [policies[x] for g in p["groups"] for x in groups[g]]
        boundary = boundaries.get(p["permission_boundary"]) if p["permission_boundary"] else None
        qs, answers = [], []
        # Build a pool of candidate requests from the principal's own statements
        # (resources instantiated to match), then choose five: up to two where a
        # naive evaluator -- no conditions, no boundary -- gets it wrong, and the
        # rest balanced between allow and deny.
        own = [st for d in docs for st in d["Statement"]] + (boundary["Statement"] if boundary else [])

        def instantiate(st):
            svc = st["Action"][0].split(":")[0].lower()
            act = st["Action"][0].split(":")[1]
            act = next((a for a in SERVICES[svc] if a.lower() == act.lower()), None) or prng.choice(SERVICES[svc])
            res = st["Resource"][0]
            if "*" in res:
                tail = {"s3": prng.choice(["2026/q3.csv", "archive/Q3.CSV", "tmp/x.parquet"]),
                        "dynamodb": prng.choice(TABLES), "kms": prng.choice(["billing", "data"]),
                        "logs": prng.choice(["api", "audit"])}[svc]
                res = res.replace("*", tail if not res.endswith(":::*") else f"{prng.choice(BUCKETS)}/{tail}", 1)
            if prng.random() < 0.4:
                res = recase(res)  # resources match case-sensitively
            return f"{svc}:{act}", res

        pool = []
        for _ in range(120):
            if own and prng.random() < 0.85:
                action, res = instantiate(prng.choice(own))
            else:
                svc = prng.choice(list(SERVICES))
                action, res = f"{svc}:{prng.choice(SERVICES[svc])}", resource(prng, svc)
            ctx = {"ip": prng.choice(["10.20.30.40", "192.168.10.7", "203.0.113.9"]),
                   "time": prng.choice(["2026-03-15T09:00:00Z", "2026-09-26T10:00:00Z"]), "tags": p["tags"]}
            if prng.random() < 0.5:  # a context that satisfies common conditions
                ctx["ip"] = prng.choice(["10.20.30.40", "192.168.10.7"])
                ctx["time"] = "2026-03-15T09:00:00Z"
            true = evaluate(docs, boundary, action, res, ctx)
            naive = evaluate([{"Statement": [dict(st, Condition=None) for d in docs for st in d["Statement"]]}],
                             None, action, res, ctx)
            folded = evaluate([{"Statement": [dict(st, Resource=[r.lower() for r in st["Resource"]]) for st in d["Statement"]]}
                               for d in docs], boundary, action, res.lower(), ctx)
            pool.append((action, res, ctx, true, naive, folded))
        # One question a naive evaluator gets wrong, one that case-folding gets
        # wrong, then balance allow and deny.
        chosen = [c for c in (next((c for c in pool if c[3] != c[4]), None),
                              next((c for c in pool if c[3] != c[5]), None)) if c]
        for want in ["allow", "deny", "allow", "deny", "allow"]:
            if len(chosen) == 5:
                break
            pick = next((c for c in pool if c[3] == want and c not in chosen), None) or next(c for c in pool if c not in chosen)
            chosen.append(pick)
        prng.shuffle(chosen)
        qs = [f"{q + 1}. `{a}` on `{r}` from `{c['ip']}` at `{c['time']}`" for q, (a, r, c, *_) in enumerate(chosen)]
        answers = [c[3] for c in chosen]
        files[f"questions/{name}.md"] = f"# Access questions for `{name}`\n\n" + "\n".join(qs) + "\n"
        truth["principals"][name] = {"answers": answers, "unit_chars": 5000}
    files["iam/principals.json"] = json.dumps(principals, indent=2) + "\n"
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


EVALUATION = """# How access is evaluated

For a request (principal, action, resource, source IP, time):

1. Collect the principal's own policies (`iam/principals.json`) and all
   policies of every group it belongs to (`iam/groups.json`).
2. A statement matches when its Action, its Resource and all of its Conditions match:
   - Action patterns match case-insensitively; `*` matches any run of
     characters and `?` any single character.
   - Resource patterns match case-sensitively, with the same wildcards.
   - `IpAddress` / `aws:SourceIp`: the source IP is inside the CIDR.
   - `StringEquals` / `aws:PrincipalTag/<key>`: the principal's tag equals the value.
   - `DateLessThan` / `aws:CurrentTime`: the request time is before the value.
3. If any matching statement has Effect `Deny`, the answer is **deny**.
4. Otherwise, if no matching statement has Effect `Allow`, the answer is **deny**.
5. Otherwise, if the principal has a `permission_boundary`, the boundary
   policy (in `iam/policies/`) must also have a matching Allow; if not, **deny**.
6. Otherwise **allow**.
"""


def grade(seed, answer):
    """Per principal, all or nothing: all five answers right. Reward is the mean."""
    truth = generate(seed)
    per = {}
    for name, t in truth["principals"].items():
        got = answer.get(name) if isinstance(answer.get(name), list) else []
        per[name] = float(got == t["answers"])
    return {"reward": round(sum(per.values()) / len(per), 4), "principals": per}


def oracle(seed):
    return {n: t["answers"] for n, t in generate(seed)["principals"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["principals"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(EVALUATION) + 4000}


ANSWER_PATH = "/workspace/answer/access.json"
INSTRUCTION = """\
# Access review

The auditors sent access questions for every principal: see
`/workspace/questions/`. Answer each one from the IAM documents in `iam/`,
evaluated exactly as `docs/EVALUATION.md` describes.

Write `/workspace/answer/access.json`, one list of five answers per principal,
in question order:

```json
{"<principal>": ["allow", "deny", "deny", "allow", "deny"]}
```
"""

META = {
    "unit": "principal", "kind": "access decisions", "domain": "IAM policies", "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "exact policy evaluation over each principal's own set of documents",
    "deliverable": "`/workspace/answer/access.json`",
    "grading": "Per principal, all or nothing: all five answers right. Reward is the mean.",
    "per_unit": "collect the principal's direct and group policies and boundary, then evaluate five requests "
                "through wildcards, conditions, explicit denies and the boundary",
    "traps": [
        "**Explicit deny wins**, often from a group policy.",
        "**Permission boundaries** cut allows the policies grant.",
        "**Case**: actions match case-insensitively, resources case-sensitively (`Q3.CSV`).",
        "**Conditions**: IP ranges, team tags, and dates that expired before the request.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
