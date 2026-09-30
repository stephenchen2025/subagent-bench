#!/usr/bin/env python3
"""LH35 -- investigate 48 food-borne outbreaks: cases, vehicle, risk ratio.

outbreaks/OB-NN/ is one event -- a wedding, a school lunch, a conference
dinner: event.md (when the meal was served, the menu) and questionnaires.csv
(one row per attendee: what they ate, their symptoms in their own words, when
they fell ill). docs/CASE_DEFINITION.md fixes the analysis, the same for every
event:

- a case fell ill 6 to 72 hours after the meal, with vomiting or diarrhoea
  (however they wrote it); nausea or a headache alone is not a case;
- someone ill outside that window, or ill with no onset time, is excluded;
- a blank answer about a food leaves that person out of that food's table;
- the vehicle is the food with the highest risk ratio among foods that at
  least 60% of the cases ate.

    python3 lh35_outbreak_investigation.py --seed 1 --out /fixture
"""

import csv
import datetime as dt
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_EVENTS = 48
FOODS = ["chicken curry", "rice salad", "egg mayonnaise sandwiches", "prawn cocktail", "roast beef", "green salad",
         "chocolate mousse", "fruit salad", "cheese board", "tiramisu", "coleslaw", "potato salad", "salmon terrine",
         "garlic bread", "lemon tart", "hummus"]
QUALIFYING = ["diarrhoea", "vomiting", "loose stools", "watery stools", "threw up", "being sick", "the runs"]
NONQUALIFYING = ["nausea", "headache", "tiredness", "stomach ache", "felt queasy"]
EVENTS = ["wedding reception", "school lunch", "conference dinner", "christening buffet", "retirement party",
          "sports club barbecue"]


def is_case_symptom(text):
    t = text.lower()
    return any(q in t for q in QUALIFYING)


def analyse(meal, rows, foods):
    """docs/CASE_DEFINITION.md, exactly."""
    status = {}
    for r in rows:
        if r["attended"].strip().upper() != "Y":  # a household contact, not at the meal
            status[r["id"]] = "excluded"
            continue
        sym = r["symptoms"].strip()
        if not sym or sym.lower() == "none":
            status[r["id"]] = "noncase"
            continue
        if not is_case_symptom(sym):
            status[r["id"]] = "noncase"
            continue
        if not r["onset"]:
            status[r["id"]] = "excluded"
            continue
        hours = (dt.datetime.strptime(r["onset"], "%Y-%m-%d %H:%M") - meal).total_seconds() / 3600
        status[r["id"]] = "case" if 6 <= hours <= 72 else "excluded"
    cases = [r for r in rows if status[r["id"]] == "case"]
    best = None
    for f in foods:
        col = f"ate_{f.replace(' ', '_')}"
        cells = {"a": 0, "b": 0, "c": 0, "d": 0}  # exposed case, exposed non-case, unexposed case, unexposed non-case
        for r in rows:
            s, ans = status[r["id"]], r[col].strip().upper()
            if s == "excluded" or ans not in ("Y", "N"):
                continue
            key = ("a" if s == "case" else "b") if ans == "Y" else ("c" if s == "case" else "d")
            cells[key] += 1
        ate_cases = sum(1 for r in cases if r[col].strip().upper() == "Y")
        if not cases or ate_cases / len(cases) < 0.6:
            continue
        a, b, c, d = cells["a"], cells["b"], cells["c"], cells["d"]
        if 0 in (a, b, c, d):
            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        rr = (a / (a + b)) / (c / (c + d))
        if best is None or rr > best[1]:
            best = (f, rr)
    return {"cases": len(cases), "vehicle": best[0] if best else None, "rr": best[1] if best else None}


def build_event(rng, eid):
    foods = rng.sample(FOODS, rng.randint(6, 9))
    vehicle = rng.choice(foods)
    staple = rng.choice([f for f in foods if f != vehicle])  # eaten by nearly everyone
    rare = rng.choice([f for f in foods if f not in (vehicle, staple)])  # few ate it
    meal = dt.datetime(2026, rng.randint(3, 9), rng.randint(1, 26), rng.choice([12, 13, 18, 19, 20]), rng.choice([0, 30]))
    rows = []
    for i in range(rng.randint(45, 90)):
        ate = {}
        for f in foods:
            p = 0.92 if f == staple else 0.12 if f == rare else rng.uniform(0.35, 0.7)
            ate[f] = rng.random() < p
        risk = 0.7 if ate[vehicle] else 0.06
        ill = rng.random() < risk
        onset, sym = "", rng.choice(["", "none", "", rng.choice(NONQUALIFYING)])
        if ill:
            sym = ", ".join(rng.sample(QUALIFYING, rng.randint(1, 2)) + rng.sample(NONQUALIFYING, rng.randint(0, 1)))
            h = rng.uniform(4, 80) if rng.random() < 0.2 else rng.uniform(8, 48)
            onset = "" if rng.random() < 0.05 else (meal + dt.timedelta(hours=h)).strftime("%Y-%m-%d %H:%M")
        row = {"id": f"{eid}-{i + 1:03d}", "attended": "Y", "symptoms": sym, "onset": onset}
        for f in foods:
            row[f"ate_{f.replace(' ', '_')}"] = "" if rng.random() < 0.04 else ("Y" if ate[f] else "N")
        rows.append(row)
    # Household contacts reported by ill attendees: at home, not at the meal, often
    # ill a day or two later (secondary spread). They must not count.
    for j in range(rng.randint(4, 9)):
        row = {"id": f"{eid}-H{j + 1:02d}", "attended": "N",
               "symptoms": ", ".join(rng.sample(QUALIFYING, rng.randint(1, 2))),
               "onset": (meal + dt.timedelta(hours=rng.uniform(30, 70))).strftime("%Y-%m-%d %H:%M")}
        for f in foods:
            row[f"ate_{f.replace(' ', '_')}"] = rng.choice(["", "N", "Y"])  # leftovers brought home
        rows.append(row)
    rng.shuffle(rows)
    return meal, foods, rows


def to_csv(rows, foods):
    out = io.StringIO()
    fields = ["id", "attended"] + [f"ate_{f.replace(' ', '_')}" for f in foods] + ["symptoms", "onset"]
    w = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


CASE_DEFINITION = """# Case definition and analysis

0. **Attendees only.** Questionnaires also came back from household contacts
   who were not at the meal (`attended` = N). They are excluded from everything.
1. **Case:** an attendee whose symptoms include vomiting or diarrhoea (in any
   wording: "loose stools", "threw up", "being sick", "the runs", ...) with
   onset from 6 to 72 hours (inclusive) after the meal was served.
2. **Non-case:** an attendee with no symptoms, or only other symptoms (nausea,
   headache, stomach ache, tiredness).
3. **Excluded:** an attendee with vomiting or diarrhoea whose onset is outside
   the window, or not recorded. Excluded people are left out of every table.
4. **Tables:** for each food, exposed = answered Y, unexposed = answered N; a
   blank answer leaves that person out of that food's table only.
   Attack rate = cases / (cases + non-cases). Risk ratio = attack rate among
   the exposed / attack rate among the unexposed. If any of the four cells is
   0, add 0.5 to all four before computing.
5. **Vehicle:** among the foods eaten by at least 60% of the cases, the one
   with the highest risk ratio.
"""


def generate(seed, out=None):
    files = {"docs/CASE_DEFINITION.md": CASE_DEFINITION}
    truth = {"seed": seed, "events": {}}
    for i in range(N_EVENTS):
        eid = f"OB-{i + 1:02d}"
        rng = rng_for(seed, "event", eid)
        for _ in range(100):
            meal, foods, rows = build_event(rng, eid)
            text = to_csv(rows, foods)
            result = analyse(meal, list(csv.DictReader(io.StringIO(text))), foods)
            if result["vehicle"] and result["cases"] >= 8:
                break
        kind = rng.choice(EVENTS)
        files[f"outbreaks/{eid}/event.md"] = (
            f"# {eid}: {kind}\n\n- Meal served: {meal:%Y-%m-%d %H:%M}\n- Menu: {', '.join(foods)}\n"
            f"- Questionnaires returned: {len(rows)}\n")
        files[f"outbreaks/{eid}/questionnaires.csv"] = text
        truth["events"][eid] = dict(result, unit_chars=len(text) + 2500)
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def grade(seed, answer):
    """Per event, all or nothing: the number of cases, the vehicle, and its
    risk ratio within 1 %."""
    truth = generate(seed)
    per = {}
    for eid, t in truth["events"].items():
        got = answer.get(eid) if isinstance(answer.get(eid), dict) else {}
        try:
            ok = (got.get("cases") == t["cases"] and str(got.get("vehicle", "")).strip().lower() == t["vehicle"]
                  and abs(float(got["rr"]) - t["rr"]) <= 0.01 * t["rr"])
        except (KeyError, TypeError, ValueError):
            ok = False
        per[eid] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "events": per}


def oracle(seed):
    return {eid: {k: t[k] for k in ("cases", "vehicle", "rr")} for eid, t in generate(seed)["events"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["events"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(CASE_DEFINITION) + 300}


ANSWER_PATH = "/workspace/answer/outbreaks.json"
INSTRUCTION = """\
# Outbreak line lists for the regional health team

Every folder in `/workspace/outbreaks/` is one reported food-borne outbreak:
the event and its attendees' questionnaires. Analyse each by
`docs/CASE_DEFINITION.md`: count the cases, and name the vehicle with its
risk ratio.

Write `/workspace/answer/outbreaks.json`:

```json
{"OB-NN": {"cases": 0, "vehicle": "food as written on the menu", "rr": 0.0}}
```
"""

META = {
    "unit": "outbreak", "kind": "outbreak attribution", "domain": "food-borne epidemiology",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "a case definition applied to free-text answers, then an analysis that one misclassified person moves",
    "deliverable": "`/workspace/answer/outbreaks.json`",
    "grading": "Per event, all or nothing: the number of cases, the vehicle, and its risk ratio within 1 %. "
               "Reward is the mean.",
    "per_unit": "classify every attendee by symptoms and onset window, build a 2x2 table per food leaving out "
                "blanks and excluded people, and pick the vehicle by risk ratio among foods most cases ate",
    "traps": [
        "**Symptoms in free text**: \"the runs\", \"being sick\" count; nausea alone does not.",
        "**The onset window**: ill 5 hours after the meal, or on day four, is excluded, not a case.",
        "**Blank answers** leave a person out of that food's table only.",
        "**Household contacts** who were not at the meal (attended = N) fall ill later and must be excluded.",
        "**Zero cells** need the 0.5 correction.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
