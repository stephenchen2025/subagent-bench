#!/usr/bin/env python3
"""LH25 -- triage 80 support tickets by the support policy.

tickets/T-*.md are this morning's queue. For each, docs/SUPPORT_POLICY.md
determines five fields, and each needs a fact from somewhere else:

- `category` -- from the ticket's content, not its keywords ("how do I turn on
  2FA" is how_to, not security; "I think someone logged into my account" is);
- `priority` -- plan x severity from a matrix; the customer's plan is in
  accounts.csv, never in the ticket;
- `route` -- security and data loss go to security, bugs to engineering,
  refunds above EUR 500 to finance (amounts are sometimes in other currencies,
  converted at the policy's rates), and a duplicate is merged;
- `kb_article` -- the knowledge-base article whose symptoms match (kb/),
  identified by error code or behaviour, or null when none does;
- `duplicate_of` -- the same customer's earlier ticket about the same issue
  within 48 hours; 49 hours later is a new ticket.

    python3 lh25_ticket_triage.py --seed 1 --out /fixture
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_TICKETS = 80
SEVERITY = {"security": "critical", "data_loss": "critical", "bug": "high", "account_access": "high",
            "billing": "medium", "how_to": "low", "feature_request": "low"}
MATRIX = {"enterprise": {"critical": "P1", "high": "P1", "medium": "P2", "low": "P3"},
          "pro": {"critical": "P1", "high": "P2", "medium": "P3", "low": "P4"},
          "free": {"critical": "P2", "high": "P3", "medium": "P4", "low": "P4"}}
FX = {"EUR": 1.0, "USD": 0.92, "GBP": 1.17}
KB = {
    "KB-101": ("Exports fail with E-4012", "CSV exports stop at 10,000 rows and show error E-4012.", "bug"),
    "KB-102": ("Sync stuck on 'Pending'", "Mobile sync shows 'Pending' forever after an app update.", "bug"),
    "KB-103": ("Enabling two-factor authentication", "How to turn on 2FA from Settings > Security.", "how_to"),
    "KB-104": ("Resetting a forgotten password", "Password reset emails and what to do if they do not arrive.", "account_access"),
    "KB-105": ("Changing billing currency", "How to switch the invoice currency.", "how_to"),
    "KB-106": ("Duplicate charges after plan change", "A plan change can show two charges; the older is voided in 3 days.", "billing"),
    "KB-107": ("Webhook deliveries return 410", "Webhooks to deleted endpoints fail with HTTP 410.", "bug"),
    "KB-108": ("Account locked after failed logins", "Five failed logins lock the account for 30 minutes.", "account_access"),
    "KB-109": ("Recovering deleted projects", "Deleted projects are recoverable for 30 days from Trash.", "data_loss"),
}
TEMPLATES = {
    "bug": [("Export broken", "Every time I export our orders to CSV it stops early and shows E-4012. We need the full file.", "KB-101"),
            ("Mobile app never syncs", "Since the update yesterday the phone app just says Pending and never finishes syncing.", "KB-102"),
            ("Webhooks failing", "Our webhook calls are all coming back 410 since this morning.", "KB-107"),
            ("Charts render blank", "The revenue chart on the dashboard is just an empty box in Firefox.", None)],
    "how_to": [("2FA setup", "How do I turn on two-factor authentication for my team? Security asked us to.", "KB-103"),
               ("Invoice currency", "Can we get our invoices in EUR instead of USD? Where do I change that?", "KB-105"),
               ("Bulk tagging", "Is there a way to tag many orders at once?", None)],
    "security": [("Suspicious login", "I got a login alert from a country I have never been to, and my API keys page shows a key I did not create.", None),
                 ("Leaked token?", "One of our API tokens appeared in a public GitHub repo. Is our data exposed?", None)],
    "data_loss": [("Project disappeared", "Our whole Q3 project is gone from the list. Nobody on the team deleted it on purpose.", "KB-109"),
                  ("Records missing after import", "After yesterday's import half of our customer records are simply missing.", None)],
    "account_access": [("Locked out", "I tried my password a few times and now it says my account is locked.", "KB-108"),
                       ("No reset email", "I requested a password reset three times and no email arrives.", "KB-104")],
    "billing": [("Charged twice", "After upgrading we see two charges on the card this month.", "KB-106"),
                ("Refund request", "We cancelled within the trial but were charged {amount}. Please refund it.", None)],
    "feature_request": [("Dark mode", "Would love a dark mode for the dashboard.", None),
                        ("SSO with Okta", "Please support Okta SSO for our workspace.", None)],
}

POLICY = f"""# Support policy

For every ticket decide:

- **category**: one of {", ".join(f"`{c}`" for c in SEVERITY)}. Classify by what
  the customer is experiencing: a question about how to use a security feature
  is `how_to`; a suspected compromise is `security`; lost or missing data is
  `data_loss`.
- **priority**: from the customer's plan (see `accounts.csv`) and the category's severity:

| severity by category | {" | ".join(f"{c}: {s}" for c, s in SEVERITY.items())} |
|---|---|

| plan | critical | high | medium | low |
|---|---|---|---|---|
""" + "\n".join(f"| {p} | {r['critical']} | {r['high']} | {r['medium']} | {r['low']} |" for p, r in MATRIX.items()) + f"""

- **route**: `security` for security and data_loss; `engineering` for bugs;
  `finance` for refund requests above EUR 500 (convert at EUR per unit:
  {", ".join(f"{c} {r}" for c, r in FX.items())}); `merge` for duplicates;
  `support` for everything else.
- **kb_article**: the knowledge-base article in `kb/` that addresses the
  customer's problem, or null if none does.
- **duplicate_of**: if the same customer opened a ticket about the same issue
  within the previous 48 hours, that ticket's id (and route `merge`); else null.
  A duplicate keeps the category, priority and kb_article of the original.
"""


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    customers = [f"{n}@{d}" for n in ("ops", "admin", "finance", "it", "ceo", "dev", "sam", "lee", "kim", "ana")
                 for d in ("northwind.io", "globex.com", "initech.net", "hooli.dev", "vandelay.co")]
    plans = {c: rng.choice(["free", "pro", "pro", "enterprise"]) for c in customers}
    files = {"docs/SUPPORT_POLICY.md": POLICY,
             "accounts.csv": "email,plan,region\n" + "".join(f"{c},{p},{rng.choice(['eu', 'us'])}\n" for c, p in plans.items())}
    for kid, (title, body, _) in KB.items():
        files[f"kb/{kid}.md"] = f"# {kid}: {title}\n\n{body}\n"
    tickets, truth = [], {"seed": seed, "tickets": {}}
    t0 = dt.datetime(2026, 9, 21, 8, 0)
    cats = list(TEMPLATES)
    for i in range(N_TICKETS):
        trng = rng_for(seed, "t", i)
        tid = f"T-{5100 + i}"
        when = t0 + dt.timedelta(minutes=trng.randint(0, 5 * 24 * 60))
        dup_src = [t for t in tickets if not t["dup"]] if i > 5 and trng.random() < 0.18 else []
        if dup_src:
            src = trng.choice(dup_src)
            gap = trng.choice([trng.randint(1, 47), trng.randint(49, 90)])
            when = src["when"] + dt.timedelta(hours=gap, minutes=trng.randint(0, 50))
            within = gap < 48
            t = {**src, "id": tid, "when": when, "dup": within, "orig": src["id"] if within else None,
                 "subject": "Re: " + src["subject"], "body": "Following up -- still happening. " + src["body"]}
        else:
            cat = trng.choice(cats)
            subject, body, kb = trng.choice(TEMPLATES[cat])
            amount, ccy = None, None
            if "{amount}" in body:
                ccy = trng.choice(list(FX))
                amount = trng.choice([120, 380, 560, 610, 900, 1500])
                body = body.replace("{amount}", f"{ccy} {amount}")
            t = {"id": tid, "when": when, "customer": trng.choice(customers), "cat": cat, "kb": kb,
                 "subject": subject, "body": body, "amount": amount, "ccy": ccy, "dup": False, "orig": None}
        tickets.append(t)
    for t in tickets:
        files[f"tickets/{t['id']}.md"] = (f"# {t['id']}: {t['subject']}\n\n- From: {t['customer']}\n"
                                          f"- Received: {t['when']:%Y-%m-%d %H:%M} UTC\n\n{t['body']}\n")
        plan = plans[t["customer"]]
        if t["dup"]:
            route = "merge"
        elif t["cat"] in ("security", "data_loss"):
            route = "security"
        elif t["cat"] == "bug":
            route = "engineering"
        elif t["amount"] and t["amount"] * FX[t["ccy"]] > 500:
            route = "finance"
        else:
            route = "support"
        truth["tickets"][t["id"]] = {"category": t["cat"], "priority": MATRIX[plan][SEVERITY[t["cat"]]],
                                     "route": route, "kb_article": t["kb"], "duplicate_of": t["orig"],
                                     "unit_chars": 3500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


FIELDS = ["category", "priority", "route", "kb_article", "duplicate_of"]


def grade(seed, answer):
    """Per ticket, all five fields must be right. Reward is the mean."""
    truth = generate(seed)
    per = {}
    for tid, t in truth["tickets"].items():
        got = answer.get(tid) if isinstance(answer.get(tid), dict) else {}
        per[tid] = float(all(got.get(f) == t[f] for f in FIELDS))
    return {"reward": round(sum(per.values()) / len(per), 4), "tickets": per}


def oracle(seed):
    return {tid: {f: t[f] for f in FIELDS} for tid, t in generate(seed)["tickets"].items()}


def solve(seed, path):
    import json
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["tickets"].values()],
            "judgement_turns": 3, "orchestration_turns": 10, "shared_chars": len(POLICY) + 2500}


ANSWER_PATH = "/workspace/answer/triage.json"
INSTRUCTION = """\
# Morning queue triage

Triage every ticket in `/workspace/tickets/` according to
`docs/SUPPORT_POLICY.md`. Customer plans are in `accounts.csv`; the knowledge
base is in `kb/`.

Write `/workspace/answer/triage.json`:

```json
{"T-NNNN": {"category": "...", "priority": "P1", "route": "...", "kb_article": "KB-NNN" or null,
            "duplicate_of": "T-NNNN" or null}}
```
"""

META = {
    "unit": "ticket", "kind": "triage routing", "domain": "customer support", "output_tokens": 900, "needs_pytest": False,
    "failure_mode": "multi-source judgement per item: content, customer record, policy matrix, knowledge base, history",
    "deliverable": "`/workspace/answer/triage.json`",
    "grading": "Per ticket, all five fields right. Reward is the mean.",
    "per_unit": "classify the problem by what the customer experiences, look up the plan, apply the matrix, "
                "pick the matching KB article, check the refund threshold and the customer's recent tickets",
    "traps": [
        "**Keywords mislead**: a 2FA how-to mentions security.",
        "**Plans are only in accounts.csv.**",
        "**Refund thresholds** after currency conversion.",
        "**48 hours**: a follow-up 49 hours later is a new ticket, not a duplicate.",
        "**KB matches by symptom**, and some problems have no article.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
