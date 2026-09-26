#!/usr/bin/env python3
"""LH21 -- clean 46 raw exports, each to its own written spec.

data/<name>/raw.csv is an export from one of the systems being migrated;
data/<name>/SPEC.md says, step by step, how to turn it into the clean file the
new system imports. The deliverable is clean/<name>.csv, exactly as the spec
defines it: columns, values, which rows survive, and their order.

Specs draw from a shared pool of steps but pick different ones, in different
orders, with different parameters, so every dataset is its own job:

- phone numbers to E.164 with the dataset's default country code;
- dates in DD/MM/YYYY vs MM/DD/YYYY vs "3 Sep 2026" into ISO;
- de-duplication by a key, keeping the most recently updated row;
- enum synonyms (Y / yes / TRUE / 1) into one canonical value;
- names split into first and last, where "van der", "de", "da" and friends
  belong to the last name;
- money in European (1.234,50) or US (1,234.50) notation into integer cents;
- emails lower-cased, with invalid ones dropping the row;
- a final sort.

Order matters: de-duplicating before or after normalising the key gives
different files, and the spec says which.

    python3 lh21_data_cleaning.py --seed 1 --out /fixture
"""

import csv
import io
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_DATASETS = 46
FIRST = ["Jan", "Anna", "Pieter", "Marie", "Luca", "Sofia", "Tom", "Eva", "Noah", "Lena", "Hugo", "Iris"]
LAST = ["Berg", "Silva", "Rossi", "Smith", "Meyer", "Jansen", "Costa", "Moreau", "Novak", "Kowalski"]
PARTICLES = ["van", "van der", "de", "da", "von", "le", "di"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def raw_row(rng, i, cfg):
    first = rng.choice(FIRST)
    last = (rng.choice(PARTICLES) + " " if rng.random() < 0.4 else "") + rng.choice(LAST)
    d, mth, y = rng.randint(1, 28), rng.randint(1, 12), rng.choice([2024, 2025, 2026])
    date = {"dmy": f"{d:02d}/{mth:02d}/{y}", "mdy": f"{mth:02d}/{d:02d}/{y}", "text": f"{d} {MONTHS[mth - 1]} {y}"}[cfg["date_fmt"]]
    if rng.random() < 0.05:
        date = "unknown"
    local = f"{rng.randint(100000000, 999999999)}"
    phone = rng.choice([f"0{local}", f"+{cfg['cc']}{local}", f"00{cfg['cc']}{local}", f"({local[:3]}) {local[3:6]}-{local[6:]}",
                        "12345" if rng.random() < 0.3 else local])
    cents = rng.randint(100, 900000)
    euros, c = divmod(cents, 100)
    money = (f"€{euros:,}".replace(",", ".") + f",{c:02d}") if cfg["money_fmt"] == "eu" else f"{euros:,}.{c:02d} USD"
    email = f"{first}.{last.split()[-1]}{rng.randint(1, 99)}@Example.{rng.choice(['com', 'org', 'nl'])}"
    if rng.random() < 0.06:
        email = email.replace("@", " at ")
    status = rng.choice(cfg["synonyms"][rng.choice(list(cfg["synonyms"]))])
    key = f"C{rng.randint(1, cfg['n_keys']):04d}"
    if rng.random() < 0.2:
        key = f" {key.lower()} "
    updated = f"2026-0{rng.randint(1, 8)}-{rng.randint(10, 28)}T{rng.randint(10, 23)}:00:00"
    return {"customer_id": key, "full_name": f"  {first} {last} " if rng.random() < 0.3 else f"{first} {last}",
            "phone": phone, "signup_date": date, "amount": money, "email": email, "active": status,
            "updated_at": updated}


SYNONYMS = [{"true": ["Y", "yes", "TRUE", "1"], "false": ["N", "no", "FALSE", "0"]},
            {"active": ["A", "active", "ACTIVE", "on"], "inactive": ["I", "inactive", "off", "disabled"]}]


def spec_for(rng):
    cfg = {"cc": rng.choice(["31", "49", "33", "44", "39"]), "date_fmt": rng.choice(["dmy", "mdy", "text"]),
           "money_fmt": rng.choice(["eu", "us"]), "synonyms": rng.choice(SYNONYMS), "n_keys": rng.randint(40, 90)}
    steps = ["trim", "key_upper"]
    optional = ["phone", "date", "enum", "name", "money", "email"]
    steps += rng.sample(optional, rng.randint(3, 5))
    dedupe_pos = rng.choice(["early", "late"])
    if dedupe_pos == "early":
        steps.insert(1, "dedupe")   # before the key is normalised
    else:
        steps.append("dedupe")
    steps.append("sort")
    cfg["steps"] = steps
    cfg["sort"] = rng.choice([["customer_id"], ["signup_date", "customer_id"], ["last_name", "first_name", "customer_id"]])
    if cfg["sort"][0] == "signup_date" and "date" not in steps:
        cfg["sort"] = ["customer_id"]
    if cfg["sort"][0] == "last_name" and "name" not in steps:
        cfg["sort"] = ["customer_id"]
    return cfg


STEP_TEXT = {
    "trim": "Strip leading and trailing whitespace from every field.",
    "key_upper": "Upper-case `customer_id`.",
    "dedupe": "Keep one row per `customer_id` (compared exactly as it is at this step): the one with the "
              "latest `updated_at`; on a tie, the one that comes later in the file. Keep the surviving rows in "
              "their original relative order.",
    "phone": "Normalise `phone` to E.164: keep digits only (after noting a leading `+`); a leading `+` or `00` "
             "means the number already has a country code; a leading single `0` is replaced by country code "
             "{cc}; any other number gets {cc} prepended. Result is `+` and the digits. If the result has "
             "fewer than 10 digits, set `phone` to empty.",
    "date": "Parse `signup_date` ({datefmt}) into ISO `YYYY-MM-DD`. Drop rows whose date does not parse.",
    "enum": "Map `active` to `{a}` or `{b}` using these synonyms (exact match): {syn}. Drop rows with any other value.",
    "name": "Split `full_name` into `first_name` (the first word) and `last_name` (everything after it, "
            "including particles such as van, van der, de, da, von, le, di). Remove `full_name`.",
    "money": "Convert `amount` ({moneyfmt}) to integer cents in a column `amount_cents`. Remove `amount`.",
    "email": "Lower-case `email`. Drop rows whose email is not `local@domain.tld` (exactly one `@`, no "
             "spaces, and a dot in the domain).",
    "sort": "Sort by {sort}, ascending, comparing as plain strings (`amount_cents` numerically).",
}


def spec_md(name, cfg):
    fmt = {"dmy": "DD/MM/YYYY", "mdy": "MM/DD/YYYY", "text": "`D Mon YYYY`, e.g. 3 Sep 2026"}[cfg["date_fmt"]]
    a, b = list(cfg["synonyms"])
    syn = "; ".join(f"{k}: {', '.join(v)}" for k, v in cfg["synonyms"].items())
    lines = [f"# {name}", "", "Apply these steps in order to `raw.csv`. Write the result, with a header row, to "
             f"`clean/{name}.csv`.", ""]
    for i, s in enumerate(cfg["steps"], 1):
        lines.append(f"{i}. " + STEP_TEXT[s].format(cc=cfg["cc"], datefmt=fmt, a=a, b=b, syn=syn,
                                                    moneyfmt="European notation, e.g. €1.234,50" if cfg["money_fmt"] == "eu"
                                                    else "US notation, e.g. 1,234.50 USD",
                                                    sort=", then ".join(f"`{k}`" for k in cfg["sort"])))
    lines += ["", "Columns, in order: all remaining columns in the order they appear in `raw.csv`, with "
              "`first_name`, `last_name` in place of `full_name` and `amount_cents` in place of `amount`."]
    return "\n".join(lines) + "\n"


def clean(rows, cfg):
    import datetime as dt
    cols = list(rows[0].keys()) if rows else []
    out = [dict(r) for r in rows]
    for step in cfg["steps"]:
        if step == "trim":
            out = [{k: v.strip() for k, v in r.items()} for r in out]
        elif step == "key_upper":
            for r in out:
                r["customer_id"] = r["customer_id"].upper()
        elif step == "dedupe":
            best = {}
            for i, r in enumerate(out):
                k = r["customer_id"]
                if k not in best or r["updated_at"] >= out[best[k]]["updated_at"]:
                    best[k] = i
            keep = set(best.values())
            out = [r for i, r in enumerate(out) if i in keep]
        elif step == "phone":
            for r in out:
                p = r["phone"]
                plus = p.startswith("+")
                digits = re.sub(r"\D", "", p)
                if plus:
                    pass
                elif digits.startswith("00"):
                    digits = digits[2:]
                elif digits.startswith("0"):
                    digits = cfg["cc"] + digits[1:]
                else:
                    digits = cfg["cc"] + digits
                r["phone"] = "+" + digits if len(digits) >= 10 else ""
        elif step == "date":
            fmt = {"dmy": "%d/%m/%Y", "mdy": "%m/%d/%Y", "text": "%d %b %Y"}[cfg["date_fmt"]]
            kept = []
            for r in out:
                try:
                    r["signup_date"] = dt.datetime.strptime(r["signup_date"], fmt).date().isoformat()
                    kept.append(r)
                except ValueError:
                    pass
            out = kept
        elif step == "enum":
            back = {s: canon for canon, syns in cfg["synonyms"].items() for s in syns}
            out = [dict(r, active=back[r["active"]]) for r in out if r["active"] in back]
        elif step == "name":
            new = []
            for r in out:
                first, _, last = r["full_name"].partition(" ")
                r2 = {}
                for k, v in r.items():
                    if k == "full_name":
                        r2["first_name"], r2["last_name"] = first, last.strip()
                    else:
                        r2[k] = v
                new.append(r2)
            out = new
        elif step == "money":
            new = []
            for r in out:
                a = r["amount"]
                if cfg["money_fmt"] == "eu":
                    a = a.replace("€", "").replace(".", "").replace(",", ".")
                else:
                    a = a.replace(" USD", "").replace(",", "")
                cents = int(round(float(a) * 100))
                r2 = {}
                for k, v in r.items():
                    if k == "amount":
                        r2["amount_cents"] = str(cents)
                    else:
                        r2[k] = v
                new.append(r2)
            out = new
        elif step == "email":
            kept = []
            for r in out:
                e = r["email"].lower()
                if re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", e):
                    r["email"] = e
                    kept.append(r)
            out = kept
        elif step == "sort":
            out.sort(key=lambda r: tuple(int(r[k]) if k == "amount_cents" else r[k] for k in cfg["sort"]))
    header = list(out[0].keys()) if out else cols
    return header, out


def to_csv(header, rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=header, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    systems = ["crm", "billing", "shop", "legacy", "partner", "events", "support", "loyalty"]
    names = rng.sample([f"{s}_{k}" for s in systems for k in ("customers", "accounts", "contacts", "members", "users", "clients")], N_DATASETS)
    files = {}
    truth = {"seed": seed, "datasets": {}}
    for name in names:
        drng = rng_for(seed, "data", name)
        cfg = spec_for(drng)
        rows = [raw_row(drng, i, cfg) for i in range(drng.randint(120, 200))]
        header = list(rows[0].keys())
        files[f"data/{name}/raw.csv"] = to_csv(header, rows)
        files[f"data/{name}/SPEC.md"] = spec_md(name, cfg)
        h, clean_rows = clean(rows, cfg)
        truth["datasets"][name] = {"expected": to_csv(h, clean_rows),
                                   "unit_chars": len(files[f"data/{name}/SPEC.md"]) + 6000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
        (Path(out) / "workspace" / "clean").mkdir(parents=True, exist_ok=True)
    return truth


def grade(seed, workspace):
    """Per dataset: 0 unless the header is exact; otherwise the longest in-order
    run of exactly matching rows over the larger of expected and submitted row
    counts. Reward is the mean."""
    truth = generate(seed)
    per = {}
    for name, t in truth["datasets"].items():
        path = Path(workspace) / "clean" / f"{name}.csv"
        if not path.exists():
            per[name] = 0.0
            continue
        got = path.read_text().replace("\r\n", "\n").rstrip("\n").split("\n")
        want = t["expected"].rstrip("\n").split("\n")
        if not got or got[0] != want[0]:
            per[name] = 0.0
            continue
        prev = [0] * len(want)
        a, b = got[1:], want[1:]
        prev = [0] * (len(b) + 1)
        for x in a:
            cur = [0]
            for j, y in enumerate(b):
                cur.append(prev[j] + 1 if x == y else max(prev[j + 1], cur[j]))
            prev = cur
        per[name] = round(prev[-1] / max(len(a), len(b), 1), 4)
    return {"reward": round(sum(per.values()) / len(per), 4), "datasets": per}


def solve(seed, workspace):
    for name, t in generate(seed)["datasets"].items():
        write(Path(workspace) / "clean", f"{name}.csv", t["expected"])


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [d["unit_chars"] for d in t["datasets"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": 500}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Clean the migration exports

Every export under `/workspace/data/` has to be cleaned before the new system
can import it. Each `data/<name>/SPEC.md` says exactly how, step by step, and
the steps differ from export to export.

Write each result to `clean/<name>.csv`. The importer rejects anything that
does not match the spec exactly.
"""

META = {
    "unit": "dataset", "kind": "data transformation", "domain": "tabular data", "output_tokens": 1600, "needs_pytest": False,
    "failure_mode": "following a per-unit written procedure exactly, where step order and parameters differ",
    "deliverable": "`clean/<name>.csv` for 46 datasets",
    "grading": "Per dataset: exact header required; then the longest in-order run of exactly matching rows "
               "over the larger of expected and submitted counts. Reward is the mean.",
    "per_unit": "read the dataset's spec, implement its steps in its order with its parameters, and check "
                "the output against the raw rows",
    "traps": [
        "**Step order.** De-duplicating before the key is trimmed and upper-cased keeps different rows than after.",
        "**Parameters differ per dataset**: country code, date format, money notation, synonyms, sort keys.",
        "**Name particles** (van der, de, da) belong to the last name.",
        "**Dropping rules**: bad dates, unknown enum values and invalid emails remove the row; short phones only blank the field.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
