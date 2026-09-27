#!/usr/bin/env python3
"""Reference solution for LH34, from the workspace alone.

Reads stars/*/dips.csv and stars/*/star.md and follows docs/VETTING.md; never
sees the generator. Each worker vets one star; the orchestrator writes the
table.

    python3 solve.py /workspace
"""

import csv
import json
import math
import re
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SNR_MIN, TOL_D, R_SUN_KM, EARTH_PER_SUN = 7.1, 0.02, 695700, 109.08


def read_star(note):
    m = re.search(r"Stellar radius: ([\d.,]+) (R_sun|km)", note)
    value = float(m.group(1).replace(",", ""))
    radius = value if m.group(2) == "R_sun" else value / R_SUN_KM
    c = re.search(r"contributes (\d+)% of the measured flux", note)
    return radius, (int(c.group(1)) / 100 if c else 0.0)


def largest_period(times):
    t0 = times[0]
    for p in sorted({(t - t0) / k for t in times[1:] for k in range(1, 200) if (t - t0) / k > 0.3}, reverse=True):
        if all(abs((t - t0) / p - round((t - t0) / p)) * p <= TOL_D for t in times):
            return p
    return None


def vet_star(star_dir):
    radius, contamination = read_star((star_dir / "star.md").read_text())
    dips = sorted((float(r["time_bjd"]), float(r["depth_ppm"]))
                  for r in csv.DictReader(open(star_dir / "dips.csv")) if float(r["snr"]) >= SNR_MIN)
    if len(dips) < 3:
        return star_dir.name, {"class": "no_signal"}
    t0 = dips[0][0]
    p = largest_period([t for t, _ in dips])
    if p is None:  # no periodic signal fits every dip
        return star_dir.name, {"class": "no_signal"}
    orbits = [round((t - t0) / p) for t, _ in dips]
    period = (dips[-1][0] - t0) / orbits[-1]
    depths = [d / (1 - contamination) for _, d in dips]
    odd = [d for d, n in zip(depths, orbits) if n % 2]
    even = [d for d, n in zip(depths, orbits) if n % 2 == 0]
    mean = statistics.fmean(depths)
    if odd and even:
        mo, me = statistics.fmean(odd), statistics.fmean(even)
        if abs(mo - me) / ((mo + me) / 2) > 0.10:
            return star_dir.name, {"class": "eclipsing_binary", "period_days": round(period, 6)}
    if mean > 30000:
        return star_dir.name, {"class": "eclipsing_binary", "period_days": round(period, 6)}
    return star_dir.name, {"class": "planet", "period_days": round(period, 6),
                           "radius_earth": round(radius * EARTH_PER_SUN * math.sqrt(mean / 1e6), 4)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        rows = dict(pool.map(vet_star, sorted(d for d in (ws / "stars").iterdir() if d.is_dir())))
    out = ws / "answer" / "vetting.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"{sum(r['class'] == 'planet' for r in rows.values())} planets among {len(rows)} candidates")


if __name__ == "__main__":
    main()
