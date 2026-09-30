#!/usr/bin/env python3
"""LH36 -- check 56 teaching-lab reports: limiting reagent and yield.

reports/LR-NN.md is one student's report of a standard teaching-lab reaction:
the unbalanced skeleton equation, the two reagents as measured -- a mass of an
impure solid, a mass of a hydrate, a volume of a liquid with its density, or a
volume of a solution with its molarity -- and the mass of product isolated.
docs/YIELD_RULES.md and docs/ATOMIC_MASSES.md fix the arithmetic.

For every report: balance the equation, convert each reagent to moles of the
reacting species (a hydrate's water is not the reagent; an impure solid only
counts its pure fraction), find the limiting reagent by calculation -- some
reports claim a reagent was "in excess" when it was not -- and give the
theoretical yield of the named product and the percent yield.

    python3 lh36_reaction_yields.py --seed 1 --out /fixture
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_REPORTS = 56
MASSES = {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999, "Na": 22.990, "Mg": 24.305, "Al": 26.982,
          "S": 32.06, "Cl": 35.45, "K": 39.098, "Ca": 40.078, "Fe": 55.845, "Cu": 63.546, "Zn": 65.38,
          "Ag": 107.868, "I": 126.904, "Ba": 137.327}

# (skeleton reactants, skeleton products, balanced coefficients, product of interest)
REACTIONS = [
    (["CaCO3", "HCl"], ["CaCl2", "H2O", "CO2"], [1, 2, 1, 1, 1], "CaCl2"),
    (["Mg", "HCl"], ["MgCl2", "H2"], [1, 2, 1, 1], "MgCl2"),
    (["Fe", "CuSO4"], ["FeSO4", "Cu"], [1, 1, 1, 1], "Cu"),
    (["Zn", "CuSO4"], ["ZnSO4", "Cu"], [1, 1, 1, 1], "Cu"),
    (["Al", "CuCl2"], ["AlCl3", "Cu"], [2, 3, 2, 3], "Cu"),
    (["AgNO3", "NaCl"], ["AgCl", "NaNO3"], [1, 1, 1, 1], "AgCl"),
    (["BaCl2", "Na2SO4"], ["BaSO4", "NaCl"], [1, 1, 1, 2], "BaSO4"),
    (["Na2CO3", "CaCl2"], ["CaCO3", "NaCl"], [1, 1, 1, 2], "CaCO3"),
    (["C7H6O3", "C4H6O3"], ["C9H8O4", "C2H4O2"], [1, 1, 1, 1], "C9H8O4"),
    (["C2H6O", "C2H4O2"], ["C4H8O2", "H2O"], [1, 1, 1, 1], "C4H8O2"),
    (["NaHCO3", "C2H4O2"], ["C2H3NaO2", "H2O", "CO2"], [1, 1, 1, 1, 1], "C2H3NaO2"),
    (["Al", "O2"], ["Al2O3"], [4, 3, 2], "Al2O3"),
    (["Fe", "O2"], ["Fe2O3"], [4, 3, 2], "Fe2O3"),
    (["Na2SO4", "BaCl2"], ["NaCl", "BaSO4"], [1, 1, 2, 1], "BaSO4"),
    (["Na2CO3", "HCl"], ["NaCl", "H2O", "CO2"], [1, 2, 2, 1, 1], "NaCl"),
    (["Zn", "HCl"], ["ZnCl2", "H2"], [1, 2, 1, 1], "ZnCl2"),
    (["Mg", "O2"], ["MgO"], [2, 1, 2], "MgO"),
    (["Al", "HCl"], ["AlCl3", "H2"], [2, 6, 2, 3], "AlCl3"),
    (["Fe2O3", "CO"], ["Fe", "CO2"], [1, 3, 2, 3], "Fe"),
]
HYDRATES = {"CuSO4": 5, "Na2CO3": 10, "BaCl2": 2, "CaCl2": 2, "Na2SO4": 10, "CuCl2": 2}
LIQUIDS = {"C4H6O3": ("acetic anhydride", 1.082), "C2H6O": ("ethanol", 0.789), "C2H4O2": ("glacial acetic acid", 1.049)}
SOLUTIONS = {"HCl", "AgNO3", "CuSO4", "NaCl", "Na2SO4", "BaCl2", "CaCl2", "CuCl2"}
NAMES = {"C7H6O3": "salicylic acid", "C9H8O4": "aspirin", "C4H8O2": "ethyl acetate", "C2H3NaO2": "sodium acetate"}


def atoms(formula):
    """Count atoms in a formula like C9H8O4, Na2CO3 or CuSO4.5H2O."""
    total = {}
    for part in formula.replace("·", ".").split("."):
        mult = 1
        m = re.match(r"^(\d+)(.*)$", part)
        if m:
            mult, part = int(m.group(1)), m.group(2)
        for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", part):
            total[el] = total.get(el, 0) + mult * (int(n) if n else 1)
    return total


def molar_mass(formula):
    return sum(MASSES[el] * n for el, n in atoms(formula).items())


def check_balanced(reactants, products, coeffs):
    left, right = {}, {}
    for f, c in zip(reactants, coeffs):
        for el, n in atoms(f).items():
            left[el] = left.get(el, 0) + c * n
    for f, c in zip(products, coeffs[len(reactants):]):
        for el, n in atoms(f).items():
            right[el] = right.get(el, 0) + c * n
    assert left == right, (reactants, products, coeffs)


for _r in REACTIONS:
    check_balanced(*_r[:3])


# ------------------------------------------------------------------ one report

def reagent_line(rng, species, moles):
    """Describe `moles` of `species` the way a student measured it; returns (label, text)."""
    forms = ["pure"]
    if species in HYDRATES:
        forms += ["hydrate", "hydrate"]
    if species in LIQUIDS:
        forms = ["liquid", "liquid"]
    if species in SOLUTIONS:
        forms += ["solution"]
    if species not in LIQUIDS and species not in ("O2",):
        forms += ["impure"]
    if species == "O2":
        return "O2", f"O2 (gas), {moles * molar_mass('O2'):.3f} g consumed from the cylinder (by mass loss)"
    if species == "CO":
        return "CO", f"CO (gas), {moles * molar_mass('CO'):.3f} g consumed (by mass of gas delivered)"
    if species == "HCl" and rng.random() < 0.75:
        pct, dens = rng.choice([(37.0, 1.19), (32.0, 1.16), (36.0, 1.18)])
        return "HCl", (f"{moles * molar_mass('HCl') / (pct / 100) / dens:.2f} mL of concentrated hydrochloric acid "
                       f"({pct}% w/w HCl, density {dens} g/mL)")
    # hydrates and impure solids are the common case, not the exception
    weights = {"pure": 1, "hydrate": 9, "liquid": 1, "solution": 1, "impure": 2}
    form = rng.choices(forms, weights=[weights[f] for f in forms])[0]
    if form == "hydrate":
        h = HYDRATES[species]
        label = f"{species}·{h}H2O"
        return label, f"{moles * molar_mass(label):.3f} g of {label}"
    if form == "liquid":
        name, dens = LIQUIDS[species]
        return species, f"{moles * molar_mass(species) / dens:.2f} mL of {name} ({species}, density {dens} g/mL)"
    if form == "solution":
        molarity = rng.choice([0.100, 0.250, 0.500, 1.00, 1.50, 2.00])
        return species, f"{moles / molarity * 1000:.1f} mL of {molarity:.3f} M {species}(aq)"
    if form == "impure":
        purity = rng.choice([85.0, 90.0, 92.5, 95.0, 97.5])
        return species, f"{moles * molar_mass(species) / (purity / 100):.3f} g of {species} ({purity}% pure)"
    return species, f"{moles * molar_mass(species):.3f} g of {species}"


def parse_amount(text, species):
    """Moles of the reacting species in a reagent line (the same rules as YIELD_RULES.md)."""
    m = re.match(r"([\d.]+) g of (\S+) \(([\d.]+)% pure\)", text)
    if m:
        return float(m.group(1)) * float(m.group(3)) / 100 / molar_mass(species)
    m = re.match(r"([\d.]+) mL of .* \(\S+, density ([\d.]+) g/mL\)", text)
    if m:
        return float(m.group(1)) * float(m.group(2)) / molar_mass(species)
    m = re.match(r"([\d.]+) mL of ([\d.]+) M", text)
    if m:
        return float(m.group(1)) / 1000 * float(m.group(2))
    m = re.match(r"([\d.]+) mL of concentrated hydrochloric acid \(([\d.]+)% w/w HCl, density ([\d.]+) g/mL\)", text)
    if m:
        return float(m.group(1)) * float(m.group(3)) * float(m.group(2)) / 100 / molar_mass("HCl")
    m = re.match(r"(\S+) \(gas\), ([\d.]+) g", text)
    if m:
        return float(m.group(2)) / molar_mass(m.group(1))
    m = re.match(r"([\d.]+) g of (\S+)", text)
    return float(m.group(1)) / molar_mass(m.group(2))  # a hydrate's own molar mass, water included


def build_report(rng, reaction):
    reactants, products, coeffs, target = reaction
    scale = rng.uniform(0.004, 0.03)
    limiting = rng.randrange(2)
    ratio = rng.uniform(1.15, 1.8)
    moles = [scale * coeffs[0], scale * coeffs[1]]
    moles[1 - limiting] *= ratio
    lines = [reagent_line(rng, s, n) for s, n in zip(reactants, moles)]
    # recompute from the written numbers, exactly as a reader must
    got = [parse_amount(t, s) for (_, t), s in zip(lines, reactants)]
    extent = min(n / c for n, c in zip(got, coeffs))
    lim_idx = min(range(2), key=lambda i: got[i] / coeffs[i])
    t_index = len(reactants) + products.index(target)
    theoretical = extent * coeffs[t_index] * molar_mass(target)
    pct = rng.uniform(52, 96)
    isolated = round(theoretical * pct / 100, 3)
    excess_note = ""
    if rng.random() < 0.6:  # a note that one reagent was in excess -- usually naming the limiting one
        which = lim_idx if rng.random() < 0.7 else 1 - lim_idx
        excess_note = f"\n{reactants[which]} was used in excess."
    return {"reactants": reactants, "products": products, "target": target, "lines": lines,
            "moles": {label: n for (label, _), n in zip(lines, got)},
            "limiting": lines[lim_idx][0], "theoretical_g": theoretical,
            "percent_yield": isolated / theoretical * 100, "isolated": isolated, "note": excess_note}


def report_md(rid, r, rng):
    skel = " + ".join(r["reactants"]) + " -> " + " + ".join(r["products"])
    # Atom counts alone cannot fix the acetylation's coefficients (C, H and O
    # give only two independent constraints for four species): state them.
    written = "balanced as written" if r["reactants"] == ["C7H6O3", "C4H6O3"] else "unbalanced"
    product = r["target"] + (f" ({NAMES[r['target']]})" if r["target"] in NAMES else "")
    lines = [f"# {rid}", "", f"Reaction ({written}): {skel}", "", "Reagents:", ""]
    lines += [f"- {text}" for _, text in r["lines"]]
    lines += ["", f"Product collected: {r['isolated']:.3f} g of dry {product}.{r['note']}",
              "", rng.choice(["Filtered, washed and dried to constant mass.", "Dried overnight in a desiccator.",
                              "Product weighed after drying at 105 C."])]
    return "\n".join(lines) + "\n"


RULES = """# Yield rules

1. Balance the equation with the smallest whole-number coefficients. A
   reaction marked "balanced as written" has every coefficient equal to 1.
2. Convert each reagent to moles of the reacting species:
   - a mass of an impure solid: only the stated pure fraction counts;
   - a mass of a hydrate (X·nH2O): divide by the hydrate's molar mass, water
     included -- one mole of hydrate gives one mole of X;
   - a liquid: volume x density, then divide by the molar mass;
   - a solution: volume (L) x molarity;
   - concentrated acid given as % w/w with a density: volume x density x the
     mass fraction, then divide by the molar mass.
3. The limiting reagent is the one with the smallest moles / coefficient.
   Decide by calculation; a note that a reagent "was used in excess" may be wrong.
4. Theoretical yield (g) of the named product = (moles of limiting reagent /
   its coefficient) x the product's coefficient x the product's molar mass.
5. Percent yield = collected mass / theoretical yield x 100.
6. Molar masses from `ATOMIC_MASSES.md` only. Report the limiting reagent as
   it is written in the reagent list (a hydrate with its water, e.g. CuSO4·5H2O).
"""


def generate(seed, out=None):
    plan = rng_for(seed, "plan")
    order = [REACTIONS[i % len(REACTIONS)] for i in range(N_REPORTS)]
    plan.shuffle(order)
    files = {"docs/YIELD_RULES.md": RULES,
             "docs/ATOMIC_MASSES.md": "# Atomic masses (g/mol)\n\n" + "".join(f"- {k}: {v}\n" for k, v in MASSES.items())}
    truth = {"seed": seed, "reports": {}}
    for i, reaction in enumerate(order):
        rid = f"LR-{i + 1:02d}"
        rng = rng_for(seed, "report", rid)
        r = build_report(rng, reaction)
        files[f"reports/{rid}.md"] = report_md(rid, r, rng)
        truth["reports"][rid] = {"moles": r["moles"], "limiting": r["limiting"], "theoretical_g": r["theoretical_g"],
                                 "percent_yield": r["percent_yield"], "unit_chars": len(files[f"reports/{rid}.md"]) + 3000}
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def grade(seed, answer):
    """Per report, all or nothing: the moles of each reagent within 0.5 %; the
    limiting reagent; theoretical yield within 0.5 %; percent yield within 0.5
    percentage points."""
    truth = generate(seed)
    per = {}
    for rid, t in truth["reports"].items():
        got = answer.get(rid) if isinstance(answer.get(rid), dict) else {}
        try:
            got_moles = {str(k).replace(".", "·"): v for k, v in (got.get("moles") or {}).items()}
            ok = (set(got_moles) == set(t["moles"])
                  and all(abs(float(got_moles[k]) - v) <= 0.005 * v for k, v in t["moles"].items())
                  and str(got.get("limiting", "")).replace(".", "·") == t["limiting"]
                  and abs(float(got["theoretical_g"]) - t["theoretical_g"]) <= 0.005 * t["theoretical_g"]
                  and abs(float(got["percent_yield"]) - t["percent_yield"]) <= 0.5)
        except (KeyError, TypeError, ValueError):
            ok = False
        per[rid] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "reports": per}


def oracle(seed):
    return {rid: {k: t[k] for k in ("moles", "limiting", "theoretical_g", "percent_yield")}
            for rid, t in generate(seed)["reports"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2, ensure_ascii=False))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["reports"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(RULES) + 600}


ANSWER_PATH = "/workspace/answer/yields.json"
INSTRUCTION = """\
# Mark the synthesis lab reports

Each file in `/workspace/reports/` is one student's lab report. For every
report, work out the moles of each reagent, the limiting reagent, the
theoretical yield of the product and the percent yield, by
`docs/YIELD_RULES.md`. Name each reagent as the reagent list writes it.

Write `/workspace/answer/yields.json`:

```json
{"LR-NN": {"moles": {"CuSO4·5H2O": 0.0, "Zn": 0.0}, "limiting": "CuSO4·5H2O",
           "theoretical_g": 0.0, "percent_yield": 0.0}}
```
"""

META = {
    "unit": "lab report", "kind": "stoichiometry", "domain": "synthetic chemistry",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "chemical arithmetic where each report measures its reagents differently",
    "deliverable": "`/workspace/answer/yields.json`",
    "grading": "Per report, all or nothing: moles of each reagent within 0.5 %; limiting reagent; theoretical "
               "yield within 0.5 %; percent yield within 0.5 points. Reward is the mean.",
    "per_unit": "balance the equation, convert each reagent to moles (purity, hydrate water, density, molarity), "
                "compare moles per coefficient, and compute the theoretical and percent yield",
    "traps": [
        "**Coefficients**: 2 Al + 3 CuCl2 -> 2 AlCl3 + 3 Cu; 4 Fe + 3 O2 -> 2 Fe2O3.",
        "**Hydrates**: the mass includes the water of crystallisation.",
        "**Purity, density, molarity**: every reagent is measured differently.",
        "**\"Used in excess\"** notes that are wrong.",
        "**The product's coefficient** (3 Cu per 2 Al) scales the theoretical yield.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
