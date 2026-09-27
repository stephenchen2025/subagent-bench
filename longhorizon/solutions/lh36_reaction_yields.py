#!/usr/bin/env python3
"""Reference solution for LH36, from the workspace alone.

Reads reports/*.md, docs/YIELD_RULES.md and docs/ATOMIC_MASSES.md; never sees
the generator or its table of coefficients. Each worker takes one report: it
balances the skeleton equation itself (the null space of the atom matrix, in
exact fractions), converts every reagent to moles by how it was measured, and
finds the limiting reagent by calculation rather than trusting any "excess"
note.

    python3 solve.py /workspace
"""

import json
import math
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path


def load_masses(ws):
    return {el: float(v) for el, v in re.findall(r"- (\w+): ([\d.]+)", (ws / "docs" / "ATOMIC_MASSES.md").read_text())}


def atoms(formula):
    total = {}
    for part in formula.replace("·", ".").split("."):
        mult = 1
        m = re.match(r"^(\d+)(.*)$", part)
        if m:
            mult, part = int(m.group(1)), m.group(2)
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", part):
            total[el] = total.get(el, 0) + mult * (int(n) if n else 1)
    return total


def balance(reactants, products):
    """Smallest whole-number coefficients: the null space of the atom matrix."""
    species = reactants + products
    elements = sorted({el for f in species for el in atoms(f)})
    rows = [[Fraction(atoms(f).get(el, 0) * (1 if i < len(reactants) else -1)) for i, f in enumerate(species)]
            for el in elements]
    # Gaussian elimination to reduced row-echelon form
    n, pivots, r = len(species), [], 0
    for c in range(n):
        p = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        rows[r] = [x / rows[r][c] for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                rows[i] = [a - rows[i][c] * b for a, b in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivots]
    assert len(free) == 1, "expected a one-dimensional solution space"
    x = [Fraction(0)] * n
    x[free[0]] = Fraction(1)
    for i, c in enumerate(pivots):
        x[c] = -rows[i][free[0]]
    lcm = math.lcm(*[v.denominator for v in x])
    ints = [int(v * lcm) for v in x]
    g = math.gcd(*ints)
    return [abs(v // g) for v in ints]


def moles(line, masses):
    mm = lambda f: sum(masses[el] * k for el, k in atoms(f).items())  # noqa: E731
    m = re.match(r"([\d.]+) g of (\S+) \(([\d.]+)% pure\)", line)
    if m:
        return m.group(2), float(m.group(1)) * float(m.group(3)) / 100 / mm(m.group(2))
    m = re.match(r"([\d.]+) mL of .* \((\S+), density ([\d.]+) g/mL\)", line)
    if m:
        return m.group(2), float(m.group(1)) * float(m.group(3)) / mm(m.group(2))
    m = re.match(r"([\d.]+) mL of ([\d.]+) M (\S+)\(aq\)", line)
    if m:
        return m.group(3), float(m.group(1)) / 1000 * float(m.group(2))
    m = re.match(r"([\d.]+) mL of concentrated hydrochloric acid \(([\d.]+)% w/w HCl, density ([\d.]+) g/mL\)", line)
    if m:
        return "HCl", float(m.group(1)) * float(m.group(3)) * float(m.group(2)) / 100 / mm("HCl")
    m = re.match(r"(\S+) \(gas\), ([\d.]+) g", line)
    if m:
        return m.group(1), float(m.group(2)) / mm(m.group(1))
    m = re.match(r"([\d.]+) g of (\S+)", line)
    return m.group(2), float(m.group(1)) / mm(m.group(2))


def mark(path, masses):
    text = path.read_text()
    written, left, right = re.search(r"Reaction \((unbalanced|balanced as written)\): (.+) -> (.+)", text).groups()
    reactants, products = [s.strip() for s in left.split("+")], [s.strip() for s in right.split("+")]
    coeffs = [1] * (len(reactants) + len(products)) if written == "balanced as written" else balance(reactants, products)
    reagents = [moles(l, masses) for l in re.findall(r"^- (.+)$", text, re.M)]
    base = lambda label: label.split("·")[0]  # noqa: E731
    per_coeff = [(label, n / coeffs[reactants.index(base(label))]) for label, n in reagents]
    limiting, extent = min(per_coeff, key=lambda x: x[1])
    target = re.search(r"g of dry ([A-Za-z0-9]+)", text).group(1)
    collected = float(re.search(r"collected: ([\d.]+) g", text).group(1))
    mm = sum(masses[el] * k for el, k in atoms(target).items())
    theoretical = extent * coeffs[len(reactants) + products.index(target)] * mm
    return path.stem, {"moles": {label: round(n, 8) for label, n in reagents},
                       "limiting": limiting, "theoretical_g": round(theoretical, 5),
                       "percent_yield": round(collected / theoretical * 100, 3)}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    masses = load_masses(ws)
    with ThreadPoolExecutor(8) as pool:
        rows = dict(pool.map(lambda p: mark(p, masses), sorted((ws / "reports").glob("LR-*.md"))))
    out = ws / "answer" / "yields.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(rows)} reports marked")


if __name__ == "__main__":
    main()
