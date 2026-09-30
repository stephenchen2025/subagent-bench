#!/usr/bin/env python3
"""Reference solution for LH31, from the workspace alone.

It never sees the generator or the answer key: it reads what the agent reads
(runs/*/notes.md, runs/*/plate.csv, instruments.csv) and follows
docs/PROTOCOL.md. So a full score proves the task is solvable from the
workspace, not just that the grader accepts the true answers.

It is shaped the way the task is meant to be delegated:

- `analyse_run` is one subagent's job: a single run, start to finish, with no
  knowledge of the other runs. It reports the run's verdict and concentration,
  and any run its notes say it repeats.
- `orchestrate` is the orchestrator's job: fan the runs out to parallel
  workers, apply the one fact no worker can see -- that a later run replaced
  an earlier one -- and compute the summary over the valid runs only.

    python3 solve.py /workspace
"""

import csv
import json
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PARALLEL_WORKERS = 8

UNIT_TO_MG_L = {"mg/L": 1.0, "ug/mL": 1.0, "mg/dL": 10.0}   # umol/L needs the molar mass
EXCLUDE_WORDS = re.compile(r"\b(exclude|drop)\b", re.I)
WELL = re.compile(r"\b([A-H](?:1[0-2]|[1-9]))\b")


# ------------------------------------------------------------------ reading the notes

def read_notes(text):
    """Everything the protocol needs from the operator's prose."""
    facts = {"reader": None, "dilution": None, "unit": None, "molar_mass": None, "excluded": set(),
             "compromised": False, "repeats": []}
    for line in text.splitlines():
        s = line.strip().lstrip("- ").strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("Reader:"):
            facts["reader"] = s.split(":", 1)[1].strip()
            continue
        d = dilution_of(s)
        if d is not None:
            facts["dilution"] = d
        u = re.search(r"Standards are in (mg/L|ug/mL|mg/dL|umol/L)", s)
        if u:
            facts["unit"] = u.group(1)
            mm = re.search(r"molar mass ([\d.]+) g/mol", s)
            if mm:
                facts["molar_mass"] = float(mm.group(1))
        # An exclusion names its wells in a sentence that says exclude or drop;
        # a well that is only mentioned ("re-checked, keep it") stays.
        if EXCLUDE_WORDS.search(s):
            facts["excluded"].update(WELL.findall(s))
        if re.search(r"compromised|must not be reported|do not report", s, re.I):
            facts["compromised"] = True
        facts["repeats"] += re.findall(r"repeats (R-\d+)", s)
    return facts


def dilution_of(s):
    """Every wording the protocol allows, as the total dilution factor."""
    m = re.search(r"(\d+(?:\.\d+)?) uL sample \+ (\d+(?:\.\d+)?) uL", s)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return (a + b) / a
    for pattern in (r"\b1:(\d+)", r"\b1 in (\d+)", r"(\d+)-fold", r"[Dd]ilution factor (\d+)"):
        m = re.search(pattern, s)
        if m:
            return float(m.group(1))
    if re.search(r"\bundiluted\b", s, re.I):
        return 1.0
    return None


# ------------------------------------------------------------------ one run (a subagent's job)

def least_squares(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    intercept = my - slope * mx
    ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return slope, intercept, 1 - ss_res / ss_tot


def analyse_run(run_dir, linear_limits):
    """The protocol, steps 1-7, for one run. Knows nothing about other runs."""
    notes = read_notes((run_dir / "notes.md").read_text())
    result = {"run": run_dir.name, "repeats": notes["repeats"]}
    if notes["compromised"]:
        return dict(result, valid=False, reason="sample compromised (notes)")
    missing = [k for k in ("reader", "dilution", "unit") if notes[k] is None]
    if missing:
        return dict(result, valid=False, reason=f"could not read {', '.join(missing)} from the notes")

    wells = [r for r in csv.DictReader(open(run_dir / "plate.csv")) if r["well"] not in notes["excluded"]]
    blank = statistics.fmean(float(r["absorbance"]) for r in wells if r["type"] == "blank")
    factor = (UNIT_TO_MG_L[notes["unit"]] if notes["unit"] != "umol/L" else notes["molar_mass"] / 1000.0)
    limit = linear_limits[notes["reader"]]
    standards = [(float(r["conc"]) * factor, float(r["absorbance"]) - blank)
                 for r in wells if r["type"] == "standard"]
    in_range = [(c, a) for c, a in standards if a <= limit]
    if len(in_range) < 4:
        return dict(result, valid=False, reason=f"only {len(in_range)} standards within the reader's range")
    slope, intercept, r2 = least_squares([c for c, _ in in_range], [a for _, a in in_range])
    if r2 < 0.99:
        return dict(result, valid=False, reason=f"calibration R^2 {r2:.4f} below 0.99")
    sample = statistics.fmean(float(r["absorbance"]) - blank for r in wells if r["type"] == "sample")
    return dict(result, valid=True, conc_mg_l=(sample - intercept) / slope * notes["dilution"], r2=r2)


# ------------------------------------------------------------------ the orchestrator

def orchestrate(workspace):
    ws = Path(workspace)
    limits = {row["reader"]: float(row["linear_max_corrected_absorbance"])
              for row in csv.DictReader(open(ws / "instruments.csv"))}
    runs = sorted(d for d in (ws / "runs").iterdir() if d.is_dir())
    with ThreadPoolExecutor(PARALLEL_WORKERS) as pool:
        reports = {r["run"]: r for r in pool.map(lambda d: analyse_run(d, limits), runs)}

    # Only a later run's notes say it repeats an earlier one: no single worker
    # can know its own run was replaced.
    for rid, report in reports.items():
        for old in report["repeats"]:
            if old in reports and reports[old]["valid"]:
                reports[old] = dict(reports[old], valid=False, reason=f"superseded by {rid}")

    replicates = {}
    for rid, r in sorted(reports.items()):
        replicates[rid] = ({"valid": True, "conc_mg_l": round(r["conc_mg_l"], 6)} if r["valid"]
                           else {"valid": False, "reason": r["reason"]})
    valid = [r["conc_mg_l"] for r in reports.values() if r["valid"]]
    summary = {"n_valid": len(valid), "mean_mg_l": round(statistics.fmean(valid), 6),
               "sd_mg_l": round(statistics.stdev(valid), 6)}
    return {"replicates": replicates, "summary": summary}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    workspace = Path(argv[0] if argv else "/workspace")
    answer = orchestrate(workspace)
    out = workspace / "answer" / "replicates.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(answer, indent=2) + "\n")
    s = answer["summary"]
    print(f"{s['n_valid']} valid runs of {len(answer['replicates'])}: "
          f"mean {s['mean_mg_l']:.3f} mg/L, sd {s['sd_mg_l']:.3f}")


if __name__ == "__main__":
    main()
