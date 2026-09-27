#!/usr/bin/env python3
"""Reference solution for LH33, from the workspace alone.

Reads families/*.md and follows docs/INHERITANCE.md; never sees the generator.
One worker's job is one family (`modes_for`): for each mode, prune every
member's possible genotypes through each nuclear family until nothing changes;
a mode survives if nobody runs out of options. Nobody in these families marries
a relative, so the families form a tree and that pruning is exact. The
orchestrator fans families out and writes the one answer file.

    python3 solve.py /workspace
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

MODES = ["AD", "AR", "XLD", "XLR", "MT"]


def read_family(path):
    people = {}
    for line in path.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 7 or cells[0] in ("id", "---") or not line.startswith("|"):
            continue
        pid, _name, sex, father, mother, status, notes = cells
        adopted = "adopted" in notes.lower()
        married_in = "married into" in notes.lower()
        people[pid] = {"sex": sex, "status": status,
                       "father": None if father == "-" or adopted else father,
                       "mother": None if mother == "-" or adopted else mother,
                       "outside": adopted or married_in}
    return people


def genotypes(mode, sex):
    if mode == "MT" or (mode in ("XLD", "XLR") and sex == "M"):
        return {0, 1}
    return {0, 1, 2}


def is_affected(mode, sex, g):
    if mode in ("AD", "XLD", "MT"):
        return g >= 1
    if mode == "AR":
        return g == 2
    return g == (1 if sex == "M" else 2)


def gametes(g):
    return {0: {0}, 1: {0, 1}, 2: {1}}[g]


def offspring(mode, sex, gf, gm):
    if mode == "MT":
        return {gm}
    if mode in ("XLD", "XLR"):
        return set(gametes(gm)) if sex == "M" else {gf + b for b in gametes(gm)}
    return {a + b for a in gametes(gf) for b in gametes(gm)}


def mode_fits(mode, people):
    dom = {}
    for pid, p in people.items():
        opts = {g for g in genotypes(mode, p["sex"])
                if p["status"] == "not examined" or is_affected(mode, p["sex"], g) == (p["status"] == "affected")}
        if p["outside"] and p["status"] != "affected":
            opts &= {0}  # rare allele: an unaffected outsider carries none
        dom[pid] = opts
    nuclear = {}
    for pid, p in people.items():
        if p["father"] and p["mother"]:
            nuclear.setdefault((p["father"], p["mother"]), []).append(pid)
    while True:
        changed = False
        for (f, m), kids in nuclear.items():
            ok = [(a, b) for a in dom[f] for b in dom[m]
                  if all(dom[k] & offspring(mode, people[k]["sex"], a, b) for k in kids)]
            updates = {f: {a for a, _ in ok}, m: {b for _, b in ok}}
            for k in kids:
                reach = set()
                for a, b in ok:
                    reach |= offspring(mode, people[k]["sex"], a, b)
                updates[k] = dom[k] & reach
            for pid, opts in updates.items():
                if opts != dom[pid]:
                    dom[pid], changed = opts, True
            if not all(updates.values()):
                return False
        if not changed:
            return all(dom.values())


def modes_for(path):
    people = read_family(path)
    return path.stem, [m for m in MODES if mode_fits(m, people)]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        results = dict(pool.map(modes_for, sorted((ws / "families").glob("F-*.md"))))
    out = ws / "answer" / "modes.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({fid: {"modes": modes} for fid, modes in results.items()}, indent=2) + "\n")
    print(f"{len(results)} families analysed")


if __name__ == "__main__":
    main()
