#!/usr/bin/env python3
"""LH26 -- audit 56 expense reports against the travel policy.

reports/EXP-*.json are expense claims; docs/TRAVEL_POLICY.md is the policy and
docs/rates.csv the daily FX rates. For each report the brief wants the
reimbursable amount in EUR and the rules it broke. Each rule needs its own fact:

- R1 meals are capped per day at the city tier's per-diem (cities.csv maps
  cities to tiers); the excess is not reimbursed;
- R2 hotel nights are capped at the tier's nightly rate;
- R3 any line of EUR 25 or more needs a receipt, otherwise the line is rejected;
- R4 alcohol is never reimbursed: an amount noted in a line's notes as wine,
  beer or bar is deducted from that line;
- R5 meals on a Saturday or Sunday are reimbursed only on travel days (the
  report's first and last day);
- R6 business-class flights only for flights over 6 hours WITH an approval id
  in the notes; otherwise the line is reimbursed at the economy fare given in
  the notes.

Amounts convert to EUR at the rate for the line's own date, and the policy
says in which order caps, deductions and rounding apply.

    python3 lh26_expense_audit.py --seed 1 --out /fixture
"""

import datetime as dt
import json
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_REPORTS = 56
D = Decimal
CITIES = {"London": 1, "Zurich": 1, "New York": 1, "Paris": 2, "Berlin": 2, "Amsterdam": 2, "Madrid": 3,
          "Lisbon": 3, "Warsaw": 3, "Prague": 3}
PER_DIEM = {1: D("75"), 2: D("60"), 3: D("45")}
HOTEL_CAP = {1: D("260"), 2: D("190"), 3: D("140")}
CCY = {"London": "GBP", "Zurich": "CHF", "New York": "USD"}


def cents(x):
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def rates(seed):
    rng = rng_for(seed, "rates")
    out = {}
    for c, base in (("GBP", 1.17), ("CHF", 1.05), ("USD", 0.92)):
        for d in range(60):
            out[(c, dt.date(2026, 7, 1) + dt.timedelta(days=d))] = D(str(round(base * rng.uniform(0.98, 1.02), 4)))
    return out


def to_eur(amount, ccy, day, fx):
    return cents(amount * (D(1) if ccy == "EUR" else fx[(ccy, day)]))


def audit(report, fx):
    """The policy, in the order docs/TRAVEL_POLICY.md applies it."""
    city = report["city"]
    tier = CITIES[city]
    start, end = dt.date.fromisoformat(report["start"]), dt.date.fromisoformat(report["end"])
    broken, total = set(), D(0)
    meals_by_day = {}
    for line in report["lines"]:
        day = dt.date.fromisoformat(line["date"])
        eur = to_eur(D(line["amount"]), line["currency"], day, fx)
        if eur >= 25 and not line["receipt"]:
            broken.add("R3")
            continue
        notes = line.get("notes", "")
        if "alcohol:" in notes:
            alc = D(notes.split("alcohol:")[1].split()[0])
            eur -= to_eur(alc, line["currency"], day, fx)
            broken.add("R4")
        cat = line["category"]
        if cat == "meal":
            if day.weekday() >= 5 and day not in (start, end):
                broken.add("R5")
                continue
            meals_by_day[day] = meals_by_day.get(day, D(0)) + eur
            continue
        if cat == "hotel":
            nights = int(line["nights"])
            cap = HOTEL_CAP[tier] * nights
            if eur > cap:
                broken.add("R2")
                eur = cap
        if cat == "flight" and line.get("class") == "business":
            ok = float(line.get("hours", 0)) > 6 and "approval:" in notes
            if not ok:
                broken.add("R6")
                eur = to_eur(D(notes.split("economy:")[1].split()[0]), line["currency"], day, fx)
        total += eur
    for day, amount in meals_by_day.items():
        if amount > PER_DIEM[tier]:
            broken.add("R1")
            amount = PER_DIEM[tier]
        total += amount
    return str(cents(total)), sorted(broken)


def report_for(rng, rid):
    city = rng.choice(list(CITIES))
    ccy = CCY.get(city, "EUR")
    start = dt.date(2026, 7, 1) + dt.timedelta(days=rng.randint(0, 45))
    length = rng.randint(2, 6)
    end = start + dt.timedelta(days=length)
    lines = []
    for d in range(length + 1):
        day = start + dt.timedelta(days=d)
        for _ in range(rng.randint(1, 3)):
            amt = D(str(round(rng.uniform(8, 48), 2)))
            line = {"date": day.isoformat(), "category": "meal", "amount": str(amt), "currency": ccy,
                    "receipt": rng.random() > 0.12}
            if rng.random() < 0.12:
                line["notes"] = f"dinner, incl. wine -- alcohol: {round(float(amt) * rng.uniform(0.2, 0.4), 2)}"
            lines.append(line)
    lines.append({"date": start.isoformat(), "category": "hotel", "nights": length,
                  "amount": str(round(float(HOTEL_CAP[CITIES[city]]) * length * rng.uniform(0.8, 1.25), 2)),
                  "currency": ccy, "receipt": True})
    hours = round(rng.uniform(1.5, 11), 1)
    cls = rng.choice(["economy", "economy", "business"])
    fare = round(rng.uniform(150, 900), 2)
    fl = {"date": start.isoformat(), "category": "flight", "class": cls, "hours": hours, "amount": str(fare),
          "currency": "EUR", "receipt": True}
    if cls == "business":
        econ = round(fare * rng.uniform(0.3, 0.5), 2)
        fl["notes"] = f"economy: {econ}" + (f" approval: VP-{rng.randint(100, 999)}" if rng.random() < 0.5 else "")
    lines.append(fl)
    if rng.random() < 0.5:
        lines.append({"date": (start + dt.timedelta(days=1)).isoformat(), "category": "taxi",
                      "amount": str(round(rng.uniform(12, 60), 2)), "currency": ccy, "receipt": rng.random() > 0.3})
    rng.shuffle(lines)
    return {"id": rid, "employee": rng.choice(["a.berg", "m.silva", "j.novak", "s.costa", "l.meyer"]),
            "city": city, "start": start.isoformat(), "end": end.isoformat(),
            "purpose": rng.choice(["customer workshop", "conference", "offsite", "partner meeting"]), "lines": lines}


POLICY = """# Travel expense policy

Apply to each line, in this order, then to the report:

1. Convert the line to EUR at the rate for the line's date (`docs/rates.csv`,
   EUR per unit), rounded to the cent half up. EUR lines need no conversion.
2. **R3** A line of EUR 25.00 or more without a receipt is rejected entirely.
3. **R4** Alcohol is not reimbursed. If a line's notes say `alcohol: <amount>`
   (in the line's currency), convert that amount the same way and deduct it.
4. **R5** Meals on a Saturday or Sunday are rejected unless that day is the
   trip's first or last day.
5. **R2** Hotel lines are capped at the city tier's nightly rate times the
   number of nights.
6. **R6** Business-class flights are allowed only if the flight is over 6
   hours AND the notes include an `approval:` id. Otherwise the line is
   reimbursed at the `economy:` fare in its notes.
7. **R1** After all lines, meals are summed per day and each day is capped at
   the city tier's per-diem.

The reimbursable total is the sum of everything that survives. A rule is
"broken" if it rejected, reduced or capped anything in the report.

| tier | meal per-diem (EUR/day) | hotel cap (EUR/night) |
|---|---|---|
""" + "\n".join(f"| {t} | {PER_DIEM[t]} | {HOTEL_CAP[t]} |" for t in (1, 2, 3)) + "\n"


def generate(seed, out=None):
    fx = rates(seed)
    files = {"docs/TRAVEL_POLICY.md": POLICY,
             "docs/cities.csv": "city,tier\n" + "".join(f"{c},{t}\n" for c, t in CITIES.items()),
             "docs/rates.csv": "currency,date,eur_per_unit\n" + "".join(f"{c},{d},{r}\n" for (c, d), r in sorted(fx.items()))}
    truth = {"seed": seed, "reports": {}}
    for i in range(N_REPORTS):
        rid = f"EXP-{7000 + i * 3}"
        rep = report_for(rng_for(seed, "r", rid), rid)
        files[f"reports/{rid}.json"] = json.dumps(rep, indent=2) + "\n"
        total, broken = audit(rep, fx)
        truth["reports"][rid] = {"reimbursable_eur": total, "broken": broken,
                                 "unit_chars": len(files[f"reports/{rid}.json"]) + 1000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def grade(seed, answer):
    """Per report: 0.5 for the amount (to the cent), 0.5 for the exact set of broken rules."""
    truth = generate(seed)
    per = {}
    for rid, t in truth["reports"].items():
        got = answer.get(rid) if isinstance(answer.get(rid), dict) else {}
        try:
            amount_ok = abs(float(got.get("reimbursable_eur")) - float(t["reimbursable_eur"])) < 0.005
        except (TypeError, ValueError):
            amount_ok = False
        rules_ok = sorted(set(got.get("broken") or [])) == t["broken"]
        per[rid] = 0.5 * amount_ok + 0.5 * rules_ok
    return {"reward": round(sum(per.values()) / len(per), 4), "reports": per}


def oracle(seed):
    return {r: {"reimbursable_eur": t["reimbursable_eur"], "broken": t["broken"]}
            for r, t in generate(seed)["reports"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["reports"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(POLICY) + 3000}


ANSWER_PATH = "/workspace/answer/expenses.json"
INSTRUCTION = """\
# Expense audit

Audit every claim in `/workspace/reports/` against `docs/TRAVEL_POLICY.md`
(city tiers in `docs/cities.csv`, FX in `docs/rates.csv`).

Write `/workspace/answer/expenses.json`:

```json
{"EXP-NNNN": {"reimbursable_eur": "1234.56", "broken": ["R1", "R3"]}}
```
"""

META = {
    "unit": "expense report", "kind": "policy audit", "domain": "expense claims", "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "applying an ordered rulebook exactly, with lookups and currency arithmetic per line",
    "deliverable": "`/workspace/answer/expenses.json`",
    "grading": "Per report: 0.5 for the reimbursable amount to the cent, 0.5 for the exact set of broken rules. "
               "Reward is the mean.",
    "per_unit": "walk every line through the ordered rules (FX at the line's date, receipts, alcohol, weekends, "
                "hotel caps, flight class), then apply daily meal caps, and total",
    "traps": [
        "**Order matters**: receipts are judged on the converted amount; meal caps apply after deductions.",
        "**Weekend meals** are fine on the first and last day.",
        "**Business class** needs both >6 hours and an approval id.",
        "**FX per line date**, not the trip start.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
