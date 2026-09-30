#!/usr/bin/env python3
"""Reference solution for LH39, from the workspace alone.

Reads plots/*/tally.csv, plots/*/notes.md and species.csv, and follows
docs/SURVEY_PROTOCOL.md; never sees the generator. Each worker takes one plot
through the protocol's five steps; the orchestrator collects the rows.

    python3 solve.py /workspace
"""

import csv
import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REQUIRED_TRAP_DAYS = 14


def load_checklist(ws):
    current, group = {}, {}
    for row in csv.DictReader(open(ws / "species.csv")):
        current[row["code"]] = row["current_code"]
        group[row["current_code"]] = row["group"]
    return current, group


def plot_area_m2(notes):
    m = re.search(r"Plot area ([\d.]+) m\^2", notes)
    if m:
        return float(m.group(1))
    m = re.search(r"Plot area ([\d.]+) ha", notes)
    if m:
        return float(m.group(1)) * 10000
    m = re.search(r"Plot is ([\d.]+) m x ([\d.]+) m", notes)
    return float(m.group(1)) * float(m.group(2))


def analyse_plot(plot_dir, current, group):
    notes = (plot_dir / "notes.md").read_text()
    days = int(re.search(r"(\d+) trap-days", notes).group(1))
    if days < REQUIRED_TRAP_DAYS:
        return plot_dir.name, {"valid": False}
    counts = {}
    for row in csv.DictReader(open(plot_dir / "tally.csv")):
        code = current.get(row["code"], row["code"])
        counts[code] = counts.get(code, 0) + int(row["count"])
    for k, a, b in re.findall(r"(\d+) specimen\(s\) tallied as (\w+) were re-identified as (\w+)", notes) + \
            re.findall(r"Re-identification: (\d+) x (\w+) are actually (\w+)", notes):
        counts[a] = counts.get(a, 0) - int(k)
        counts[b] = counts.get(b, 0) + int(k)
    for k, a in re.findall(r"(\d+) (\w+) were counted twice", notes):
        counts[a] = counts.get(a, 0) - int(k)
    for a, k in re.findall(r"Double count: (\w+) is over by (\d+)", notes):
        counts[a] = counts.get(a, 0) - int(k)
    for k, a in re.findall(r"late-sorted vial added (\d+) more (\w+)", notes) + \
            re.findall(r"Add (\d+) x (\w+) from the vial", notes):
        counts[a] = counts.get(a, 0) + int(k)
    beetles = {c: n for c, n in counts.items() if group.get(c) == "beetle" and n > 0}
    total = sum(beetles.values())
    return plot_dir.name, {
        "valid": True,
        "richness": len(beetles),
        "shannon": round(-sum(n / total * math.log(n / total) for n in beetles.values()), 6),
        "simpson": round(1 - sum(n * (n - 1) for n in beetles.values()) / (total * (total - 1)), 6),
        "density_per_100m2": round(total / plot_area_m2(notes) * 100, 6),
    }


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    current, group = load_checklist(ws)
    plots = sorted(d for d in (ws / "plots").iterdir() if d.is_dir())
    with ThreadPoolExecutor(8) as pool:
        rows = dict(pool.map(lambda d: analyse_plot(d, current, group), plots))
    out = ws / "answer" / "diversity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{sum(r['valid'] for r in rows.values())} valid plots of {len(rows)}")


if __name__ == "__main__":
    main()
