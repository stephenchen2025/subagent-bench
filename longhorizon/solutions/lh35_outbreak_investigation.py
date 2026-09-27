#!/usr/bin/env python3
"""Reference solution for LH35, from the workspace alone.

Reads outbreaks/*/event.md and outbreaks/*/questionnaires.csv and follows
docs/CASE_DEFINITION.md; never sees the generator. Each worker takes one
event: classify every attendee, tabulate every food, and pick the vehicle.

    python3 solve.py /workspace
"""

import csv
import datetime as dt
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# vomiting or diarrhoea, in the wordings attendees use
QUALIFYING = re.compile(r"diarrh|vomit|loose stool|watery stool|threw up|being sick|the runs", re.I)
WINDOW_H = (6, 72)
MIN_SHARE_OF_CASES = 0.6


def classify(row, meal):
    if row["attended"].strip().upper() != "Y":
        return "excluded"
    if not QUALIFYING.search(row["symptoms"] or ""):
        return "noncase"
    if not row["onset"].strip():
        return "excluded"
    hours = (dt.datetime.strptime(row["onset"].strip(), "%Y-%m-%d %H:%M") - meal).total_seconds() / 3600
    return "case" if WINDOW_H[0] <= hours <= WINDOW_H[1] else "excluded"


def analyse_event(folder):
    meal = dt.datetime.strptime(re.search(r"Meal served: (.+)", (folder / "event.md").read_text()).group(1).strip(),
                                "%Y-%m-%d %H:%M")
    rows = list(csv.DictReader(open(folder / "questionnaires.csv")))
    status = {r["id"]: classify(r, meal) for r in rows}
    cases = [r for r in rows if status[r["id"]] == "case"]
    best = None
    for col in [c for c in rows[0] if c.startswith("ate_")]:
        if sum(r[col].strip().upper() == "Y" for r in cases) < MIN_SHARE_OF_CASES * len(cases):
            continue
        t = {("Y", "case"): 0, ("Y", "noncase"): 0, ("N", "case"): 0, ("N", "noncase"): 0}
        for r in rows:
            ans, s = r[col].strip().upper(), status[r["id"]]
            if s != "excluded" and ans in ("Y", "N"):
                t[(ans, s)] += 1
        a, b, c, d = t[("Y", "case")], t[("Y", "noncase")], t[("N", "case")], t[("N", "noncase")]
        if min(a, b, c, d) == 0:
            a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
        rr = (a / (a + b)) / (c / (c + d))
        if best is None or rr > best[1]:
            best = (col[4:].replace("_", " "), rr)
    if best is None:  # no food was eaten by enough of the cases
        return folder.name, {"cases": len(cases), "vehicle": None, "rr": None}
    return folder.name, {"cases": len(cases), "vehicle": best[0], "rr": round(best[1], 4)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        rows = dict(pool.map(analyse_event, sorted(d for d in (ws / "outbreaks").iterdir() if d.is_dir())))
    out = ws / "answer" / "outbreaks.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{len(rows)} outbreaks analysed")


if __name__ == "__main__":
    main()
