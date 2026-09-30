"""Shortcut checks for the science, mathematics and biology families (LH32-LH39).

Each function takes a fresh-workspace factory and returns the scores of the
shortcuts a hurried single agent would take on that family: the reference
solver with exactly one rule skipped, or a textbook heuristic. Every score
must stay well below a passing grade.
"""

import contextlib
import copy
import csv
import importlib
import importlib.util
import io
import json
import math
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 1


def gen(family):
    return importlib.import_module(family)


def solver(family):
    """A private copy of the family's workspace-only solver, safe to patch."""
    name = f"_solver_{family}_{id(object())}"
    spec = importlib.util.spec_from_file_location(name, ROOT / "longhorizon" / "solutions" / f"{family}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def copy_ws(ws, transform=None):
    """A copy of a workspace with `transform(text)` applied to every .md file."""
    dst = Path(tempfile.mkdtemp()) / "workspace"
    for p in ws.rglob("*"):
        if p.is_file():
            q = dst / p.relative_to(ws)
            q.parent.mkdir(parents=True, exist_ok=True)
            text = p.read_text()
            unit_file = p.suffix == ".md" and "docs" not in p.relative_to(ws).parts
            q.write_text(transform(text) if transform and unit_file else text)
    return dst


def run_main(sol, ws, answer_rel):
    with contextlib.redirect_stdout(io.StringIO()):
        sol.main([str(ws)])
    return json.loads((ws / answer_rel).read_text())


# ------------------------------------------------------------------ LH32 meta-analysis

def lh32(fresh):
    family = "lh32_meta_analysis"
    g, ws = gen(family), fresh(family)

    def score(transform=None, **patch):
        sol = solver(family)
        for k, v in patch.items():
            setattr(sol, k, v)
        return g.grade(SEED, run_main(sol, copy_ws(ws, transform), "answer/review.json"))["reward"]

    def last_row_as_week12(t):
        rows = re.findall(r"^\| (\d+) \| (.+?) \| (.+?) \|$", t, re.M)
        t = re.sub(r"^\| \d+ \| .+? \| .+? \|\n", "", t, flags=re.M)
        _, x, y = rows[-1]
        return t.rstrip("\n") + f"\n| 12 | {x} | {y} |\n"

    return [
        score(lambda t: re.sub(r"Design: .*", "Design: Randomised controlled trial.", t)),  # "randomised" substring
        score(lambda t: re.sub(  # completers as the denominators
            r"Randomised: (\d+) to (.+?), (\d+) to (.+?)\. Completed follow-up: (\d+) and (\d+)",
            lambda m: f"Randomised: {m.group(5)} to {m.group(2)}, {m.group(6)} to {m.group(4)}. "
                      f"Completed follow-up: {m.group(5)} and {m.group(6)}", t)),
        score(lambda t: re.sub(r"Registration: (\S+);",  # duplicate publications kept
                               lambda m: f"Registration: {m.group(1)}-{len(t)};", t)),
        score(last_row_as_week12),  # the last follow-up row, not week 12
        score(ACTIVE=re.compile(r"$^")),  # active comparators kept
    ]


# ------------------------------------------------------------------ LH33 pedigrees

def _pedigree_view(path, married=True, adopt=True, unexamined=False):
    people = {}
    for line in path.read_text().splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) != 7 or c[0] in ("id", "---") or not line.startswith("|"):
            continue
        pid, _, sex, father, mother, status, note = c
        adopted = note == "adopted"
        outside = note in ("married into the family", "adopted")
        bio = not (adopted and adopt)
        people[pid] = {"sex": sex, "status": "unaffected" if (unexamined and status == "not examined") else status,
                       "father": (None if father == "-" else father) if bio else None,
                       "mother": (None if mother == "-" else mother) if bio else None,
                       "founder_kind": "outside" if (married and outside and (not adopted or adopt))
                       else ("original" if father == "-" or not bio else "child")}
    return people


def lh33(fresh):
    g = gen("lh33_pedigree_inheritance")
    fams = sorted((fresh("lh33_pedigree_inheritance") / "families").glob("F-*.md"))

    def score(**kw):
        return g.grade(SEED, {p.stem: g.modes_allowed(_pedigree_view(p, **kw)) for p in fams})["reward"]

    def heuristic(p):  # "skips a generation, so recessive; only males, so X-linked"
        ppl = _pedigree_view(p)
        aff = [i for i, x in ppl.items() if x["status"] == "affected"]
        skip = any(ppl[i]["father"] and ppl[ppl[i]["father"]]["status"] != "affected"
                   and ppl[ppl[i]["mother"]]["status"] != "affected" for i in aff)
        males = all(ppl[i]["sex"] == "M" for i in aff)
        return (["XLR"] if males else ["AR"]) if skip else ["AD"]

    return [score(married=False), score(adopt=False), score(unexamined=True),
            g.grade(SEED, {p.stem: heuristic(p) for p in fams})["reward"]]


# ------------------------------------------------------------------ LH34 transits

def lh34(fresh):
    family = "lh34_transit_vetting"
    g, sol = gen(family), solver(family)
    stars = sorted(d for d in (fresh(family) / "stars").iterdir() if d.is_dir())

    def run():
        return dict(sol.vet_star(d) for d in stars)

    scores = []
    saved = sol.SNR_MIN
    sol.SNR_MIN = 0  # keep low-SNR dips
    scores.append(g.grade(SEED, run())["reward"])
    sol.SNR_MIN = saved
    read_star = sol.read_star
    sol.read_star = lambda note: (read_star(note)[0], 0.0)  # ignore dilution
    scores.append(g.grade(SEED, run())["reward"])
    sol.read_star = read_star
    base = run()
    naive = json.loads(json.dumps(base))
    for d in stars:  # period = span / (number of dips - 1)
        times = sorted(float(r["time_bjd"]) for r in csv.DictReader(open(d / "dips.csv")) if float(r["snr"]) >= 7.1)
        if naive[d.name]["class"] == "planet":
            naive[d.name]["period_days"] = (times[-1] - times[0]) / (len(times) - 1)
    scores.append(g.grade(SEED, naive)["reward"])
    km = json.loads(json.dumps(base))
    for d in stars:  # a radius in km read as solar radii
        note = (d / "star.md").read_text()
        if km[d.name]["class"] == "planet" and " km" in note:
            km[d.name]["radius_earth"] *= float(re.search(r"([\d,]+) km", note).group(1).replace(",", ""))
    scores.append(g.grade(SEED, km)["reward"])
    scores.append(g.grade(SEED, {k: ({"class": "planet"} if v["class"] == "eclipsing_binary" else v)  # no EB checks
                                 for k, v in base.items()})["reward"])
    return scores


# ------------------------------------------------------------------ LH35 outbreaks

def lh35(fresh):
    family = "lh35_outbreak_investigation"
    g, sol = gen(family), solver(family)
    events = sorted(d for d in (fresh(family) / "outbreaks").iterdir() if d.is_dir())

    def score():
        return g.grade(SEED, dict(sol.analyse_event(d) for d in events))["reward"]

    scores = []
    q = sol.QUALIFYING
    sol.QUALIFYING = re.compile(r".+")  # any symptom makes a case
    scores.append(score())
    sol.QUALIFYING = re.compile(r"diarrh|vomit", re.I)  # only the textbook words
    scores.append(score())
    sol.QUALIFYING = q
    w = sol.WINDOW_H
    sol.WINDOW_H = (0, 10 ** 6)  # no onset window
    scores.append(score())
    sol.WINDOW_H = w
    classify = sol.classify
    sol.classify = lambda row, meal: classify(dict(row, attended="Y"), meal)  # household contacts counted
    scores.append(score())
    return scores


# ------------------------------------------------------------------ LH36 reaction yields

def lh36(fresh):
    family = "lh36_reaction_yields"
    g, sol = gen(family), solver(family)
    ws = fresh(family)
    masses = sol.load_masses(ws)
    reports = sorted((ws / "reports").glob("LR-*.md"))

    def score():
        return g.grade(SEED, dict(sol.mark(p, masses) for p in reports))["reward"]

    scores = []
    balance = sol.balance
    sol.balance = lambda r, p: [1] * (len(r) + len(p))  # every coefficient 1
    scores.append(score())
    sol.balance = balance
    atoms = sol.atoms
    sol.atoms = lambda f: atoms(f.split("·")[0])  # a hydrate's water ignored
    scores.append(score())
    sol.atoms = atoms
    moles = sol.moles
    sol.moles = lambda line, m: moles(re.sub(r" \([\d.]+% pure\)", "", line), m)  # purity ignored
    scores.append(score())
    sol.moles = lambda line, m: moles(re.sub(r"\([\d.]+% w/w HCl", "(100.0% w/w HCl",  # volumes read as grams
                                             re.sub(r"density [\d.]+ g/mL", "density 1 g/mL", line)), m)
    scores.append(score())
    sol.moles = moles
    trusted = dict(sol.mark(p, masses) for p in reports)
    for p in reports:  # trust the "used in excess" note
        note = re.search(r"^(\S+) was used in excess\.", p.read_text(), re.M)
        if note:
            labels = [sol.moles(x, masses)[0] for x in re.findall(r"^- (.+)$", p.read_text(), re.M)]
            trusted[p.stem] = dict(trusted[p.stem], limiting=[x for x in labels if x.split("·")[0] != note.group(1)][0])
    scores.append(g.grade(SEED, trusted)["reward"])
    return scores


# ------------------------------------------------------------------ LH37 proofs

def lh37(fresh):
    g = gen("lh37_proof_grading")
    truth = g.generate(SEED)
    # which proofs carry a logic flaw (a valid-looking move these numbers or this domain break)
    rng = g.rng_for(SEED, "plan")
    kinds = [k for k in g.KINDS for _ in range(g.N_PROOFS // len(g.KINDS))]
    rng.shuffle(kinds)
    logic = {("arithmetic_sum", 7), ("am_gm", 1), ("irrational_root", 4), ("geometric", 5), ("common_factor", 4)}
    arithmetic_only = {}
    for i, kind in enumerate(kinds):
        pid = f"P-{i + 1:02d}"
        variant = g.rng_for(SEED, "proof", pid).choice(g.KINDS[kind][1])
        arithmetic_only[pid] = 0 if (kind, variant) in logic else truth["proofs"][pid]["first_bad_step"]
    return [g.grade(SEED, {p: 0 for p in truth["proofs"]})["reward"],  # every proof valid
            g.grade(SEED, {p: 3 for p in truth["proofs"]})["reward"],  # always the commonest step
            g.grade(SEED, arithmetic_only)["reward"]]  # checks arithmetic, not logic


# ------------------------------------------------------------------ LH38 counting

def lh38(fresh):
    """Each twist (a round table, repeated letters, replacement, "at least")
    belongs to one of eight kinds of problem, so missing just one costs about an
    eighth of the problems; the shortcut that fails is the hurried one: the
    textbook formula for each kind, with every twist ignored."""
    family = "lh38_counting_problems"
    g, sol = gen(family), solver(family)
    problems = sorted((fresh(family) / "problems").glob("Q-*.md"))
    seating, letters, urn, dice, committee, bounded, lattice = (
        sol.seating, sol.letters, sol.urn, sol.dice, sol.committee, sol.bounded_sum, sol.lattice)
    sol.seating = lambda q: seating(q.replace("round table", "row").replace("not next", "next"))
    sol.letters = lambda q: math.factorial(len(re.search(r"letters of (?:the word )?([A-Z]+)", q).group(1)))
    sol.urn = lambda q: urn(q.replace("without replacement", "with replacement"))
    sol.dice = lambda q: dice(q.replace("at least", "exactly").replace("at most", "exactly"))
    sol.committee = lambda q: committee(q.replace("refuse to serve together", ""))
    sol.bounded_sum = lambda q: bounded(re.sub(r"\d+ <= (x\d+) <= \d+", r"\1 >= 0", q))
    sol.lattice = lambda q: lattice(q.replace("never pass through", "pass through"))
    textbook = g.grade(SEED, dict(sol.solve_problem(p) for p in problems))["reward"]
    return [textbook]


# ------------------------------------------------------------------ LH39 ecology

def lh39(fresh):
    family = "lh39_ecology_surveys"
    g, sol = gen(family), solver(family)
    ws = fresh(family)
    current, group = sol.load_checklist(ws)
    plots = sorted(d for d in (ws / "plots").iterdir() if d.is_dir())
    base = dict(sol.analyse_plot(d, current, group) for d in plots)
    scores = []

    def no_corrections(d):
        keep = "\n".join(line for line in (d / "notes.md").read_text().splitlines()
                         if "trap-days" in line or "Plot" in line)
        tmp = Path(tempfile.mkdtemp()) / d.name
        tmp.mkdir()
        (tmp / "notes.md").write_text(keep)
        (tmp / "tally.csv").write_text((d / "tally.csv").read_text())
        return sol.analyse_plot(tmp, current, group)

    scores.append(g.grade(SEED, dict(no_corrections(d) for d in plots))["reward"])
    ident = {k: k for k in current}
    group2 = dict(group)
    group2.update({k: "beetle" for k, v in current.items() if group.get(v) == "beetle"})
    scores.append(g.grade(SEED, dict(sol.analyse_plot(d, ident, group2) for d in plots))["reward"])  # no synonyms
    log10 = copy.deepcopy(base)
    for row in log10.values():
        if row["valid"]:
            row["shannon"] /= math.log(10)
    scores.append(g.grade(SEED, log10)["reward"])
    everything = {k: "beetle" for k in group}
    everything["UNK"] = "beetle"
    cur = dict(current, UNK="UNK")
    scores.append(g.grade(SEED, dict(sol.analyse_plot(d, cur, everything) for d in plots))["reward"])  # all taxa
    area = copy.deepcopy(base)
    for d in plots:  # the area number read as m^2 whatever its unit
        notes, row = (d / "notes.md").read_text(), area[d.name]
        if row["valid"]:
            naive = float(re.search(r"Plot (?:area|is) ([\d.]+)", notes).group(1))
            row["density_per_100m2"] *= sol.plot_area_m2(notes) / naive
    scores.append(g.grade(SEED, area)["reward"])
    return scores


SHORTCUTS = {"lh32_meta_analysis": lh32, "lh33_pedigree_inheritance": lh33, "lh34_transit_vetting": lh34,
             "lh35_outbreak_investigation": lh35, "lh36_reaction_yields": lh36, "lh37_proof_grading": lh37,
             "lh38_counting_problems": lh38, "lh39_ecology_surveys": lh39}
