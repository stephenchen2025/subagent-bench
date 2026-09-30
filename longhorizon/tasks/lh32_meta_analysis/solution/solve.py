#!/usr/bin/env python3
"""Reference solution for LH32, from the workspace alone.

Reads reports/*.md and follows docs/REVIEW_PROTOCOL.md; never sees the
generator. Workers screen and extract one report each; the orchestrator then
resolves duplicate publications across reports (only it sees every
registration number) and pools the included trials.

    python3 solve.py /workspace
"""

import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ACTIVE = re.compile(r"sertraline|escitalopram|fluoxetine|cognitive behavioural therapy|psychotherapy|mg daily", re.I)


def screen(path):
    text = path.read_text()
    field = lambda name: re.search(rf"- {name}: (.+)", text).group(1)  # noqa: E731
    reg, year = re.search(r"Registration: (\S+); published (\d+)", text).groups()
    design, population, comparison = field("Design"), field("Participants"), field("Comparison")
    prog, n1, n2 = None, None, None
    m = re.search(r"Randomised: (\d+) to (.+?), (\d+) to (.+?)\.", text)
    n1, prog, n2, control = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)
    base = {"sid": path.stem, "reg": reg, "year": int(year), "randomised": n1 + n2}
    if re.search(r"non-randomi[sz]ed|observational|before-and-after", design, re.I) or \
            not re.search(r"randomi[sz]ed", design, re.I):
        return dict(base, include=False, reason="not randomised")
    if re.search(r"child|adolescent", population, re.I):
        return dict(base, include=False, reason="not adults")
    if ACTIVE.search(comparison.split("versus", 1)[1]):
        return dict(base, include=False, reason="active comparator")
    header = re.search(r"^\| week \| (.+?) \| (.+?) \|$", text, re.M).groups()
    row = re.search(r"^\| 12 \| (.+?) \| (.+?) \|$", text, re.M)
    if not row:
        return dict(base, include=False, reason="no week-12 outcome")
    cells = dict(zip(header, row.groups()))
    exercise_cell = cells[prog]
    control_cell = [v for k, v in cells.items() if k != prog][0]

    def events(cell, n):
        m = re.match(r"([\d.]+)%", cell)
        if m:
            return round(float(m.group(1)) * n / 100)
        return int(re.match(r"(\d+)", cell).group(1))  # "22/64" or "22 of 55 completers": the count

    a, c = events(exercise_cell, n1), events(control_cell, n2)
    if 0 in (a, n1 - a, c, n2 - c):
        a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1, n2 + 1
    log_rr = math.log((a / n1) / (c / n2))
    se = math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)
    return dict(base, include=True, log_rr=log_rr, se=se)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        rows = list(pool.map(screen, sorted((ws / "reports").glob("S-*.md"))))
    # duplicates: one report per registration number -- the most randomised, then the latest
    by_reg = {}
    for r in rows:
        by_reg.setdefault(r["reg"], []).append(r)
    for group in by_reg.values():
        if len(group) > 1:
            keep = max(group, key=lambda r: (r["randomised"], r["year"]))
            for r in group:
                if r is not keep:
                    r.update(include=False, reason=f"duplicate of {keep['sid']}")
    studies, effects = {}, []
    for r in sorted(rows, key=lambda r: r["sid"]):
        if r["include"]:
            studies[r["sid"]] = {"include": True, "log_rr": round(r["log_rr"], 6), "se": round(r["se"], 6)}
            effects.append((r["log_rr"], r["se"]))
        else:
            studies[r["sid"]] = {"include": False, "reason": r["reason"]}
    w = [1 / se ** 2 for _, se in effects]
    y = sum(wi * yi for wi, (yi, _) in zip(w, effects)) / sum(w)
    se_p = math.sqrt(1 / sum(w))
    pooled = {"k": len(effects), "rr": round(math.exp(y), 6), "ci_low": round(math.exp(y - 1.96 * se_p), 6),
              "ci_high": round(math.exp(y + 1.96 * se_p), 6)}
    out = ws / "answer" / "review.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"studies": studies, "pooled": pooled}, indent=2) + "\n")
    print(f"{pooled['k']} trials pooled: RR {pooled['rr']:.3f} ({pooled['ci_low']:.3f}-{pooled['ci_high']:.3f})")


if __name__ == "__main__":
    main()
