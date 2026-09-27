#!/usr/bin/env python3
"""LH39 -- compute the diversity of 54 ground-beetle survey plots.

plots/PL-NN/ holds one plot's pitfall-trap tally (tally.csv: species code,
count) and the observer's field notes (notes.md). species.csv is the project's
checklist: current codes, old codes that are now synonyms, and each code's
group (the survey targets ground beetles; spiders and ants also fall in).
docs/SURVEY_PROTOCOL.md fixes the procedure, the same for every plot:

1. rename synonym codes to their current code and merge them;
2. apply the observer's corrections -- specimens re-identified from one
   species to another, individuals counted twice, a late-sorted vial;
3. drop non-target groups and unidentified specimens;
4. a plot whose sampling was incomplete (a flooded or disturbed trap, fewer
   than the required trap-days) is invalid;
5. report richness, Shannon H' (natural log), Simpson's index 1 - sum
   n(n-1)/(N(N-1)), and individuals per 100 m^2 from the plot's area --
   given in m^2, hectares, or as length x width.

No two plots are alike: their species, their synonyms, the corrections in
their notes and the unit of their area all differ.

    python3 lh39_ecology_surveys.py --seed 1 --out /fixture
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_PLOTS = 54
REQUIRED_TRAP_DAYS = 14
BEETLES = ["CARNEM", "CARGRA", "PTEMEL", "PTENIG", "ABAPAR", "NEBBRE", "LORPIL", "HARRUF", "AMAAEN", "BEMLAM",
           "NOTBIG", "CALFUS", "POEVER", "AGOMUE", "LEIFER", "TRERUB"]
SYNONYMS = {"FERMEL": "PTEMEL", "CARNEMO": "CARNEM", "HARPSE": "HARRUF", "BEMBLA": "BEMLAM", "NOTBIGU": "NOTBIG"}
OTHER = {"PARAMA": "spider", "PARPUL": "spider", "MYRRUB": "ant", "LASNIG": "ant"}
NAMES = {"CARNEM": "Carabus nemoralis", "CARGRA": "Carabus granulatus", "PTEMEL": "Pterostichus melanarius",
         "PTENIG": "Pterostichus niger", "ABAPAR": "Abax parallelepipedus", "NEBBRE": "Nebria brevicollis",
         "LORPIL": "Loricera pilicornis", "HARRUF": "Harpalus rufipes", "AMAAEN": "Amara aenea",
         "BEMLAM": "Bembidion lampros", "NOTBIG": "Notiophilus biguttatus", "CALFUS": "Calathus fuscipes",
         "POEVER": "Poecilus versicolor", "AGOMUE": "Agonum muelleri", "LEIFER": "Leistus ferrugineus",
         "TRERUB": "Trechus rubens", "PARAMA": "Pardosa amentata", "PARPUL": "Pardosa pullata",
         "MYRRUB": "Myrmica rubra", "LASNIG": "Lasius niger"}


# ------------------------------------------------------------------ the protocol

def metrics(counts, area_m2):
    counts = {k: v for k, v in counts.items() if v > 0}
    n = sum(counts.values())
    shannon = -sum(v / n * math.log(v / n) for v in counts.values())
    simpson = 1 - sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))
    return {"richness": len(counts), "shannon": shannon, "simpson": simpson, "density_per_100m2": n / area_m2 * 100}


def analyse(raw, facts):
    """docs/SURVEY_PROTOCOL.md, exactly: the reference every plot is graded against."""
    if facts["trap_days"] < REQUIRED_TRAP_DAYS:
        return {"valid": False}
    counts = {}
    for code, c in raw:
        code = SYNONYMS.get(code, code)
        counts[code] = counts.get(code, 0) + c
    for kind, a, b, k in facts["corrections"]:
        if kind == "reid":
            counts[a] -= k
            counts[b] = counts.get(b, 0) + k
        elif kind == "double":
            counts[a] -= k
        elif kind == "late":
            counts[a] = counts.get(a, 0) + k
    counts = {c: v for c, v in counts.items() if c in BEETLES}
    return dict(valid=True, **metrics(counts, facts["area_m2"]))


# ------------------------------------------------------------------ one plot

def build_plot(rng, pid, invalid):
    species = rng.sample(BEETLES, rng.randint(6, 12))
    counts = {s: max(1, int(rng.lognormvariate(1.6, 0.9))) for s in species}
    raw = []
    for s, c in counts.items():
        syn = [o for o, cur in SYNONYMS.items() if cur == s]
        if syn and rng.random() < 0.6:  # the old code still used for part of the catch
            k = rng.randint(1, c) if c > 1 else 1
            raw.append((syn[0], k))
            if c - k:
                raw.append((s, c - k))
        else:
            raw.append((s, c))
    for o in rng.sample(list(OTHER), rng.randint(1, 3)):
        raw.append((o, rng.randint(1, 9)))
    if rng.random() < 0.5:
        raw.append(("UNK", rng.randint(1, 4)))
    rng.shuffle(raw)

    corrections, lines = [], []
    present = sorted(counts)
    for _ in range(rng.randint(1, 3)):
        kind = rng.choice(["reid", "double", "late"])
        a = rng.choice(present)
        have = counts[a]
        if kind == "reid" and have >= 2:
            b = rng.choice([s for s in BEETLES if s != a])
            k = rng.randint(1, have - 1)
            corrections.append(("reid", a, b, k))
            counts[a] -= k
            counts[b] = counts.get(b, 0) + k
            lines.append(rng.choice([f"{k} specimen(s) tallied as {a} were re-identified as {b} under the microscope.",
                                     f"Re-identification: {k} x {a} are actually {b} ({NAMES[b]})."]))
        elif kind == "double" and have >= 2:
            k = rng.randint(1, min(2, have - 1))
            corrections.append(("double", a, None, k))
            counts[a] -= k
            lines.append(rng.choice([f"{k} {a} were counted twice (entered from both vials); remove the duplicates.",
                                     f"Double count: {a} is over by {k}."]))
        elif kind == "late":
            k = rng.randint(1, 4)
            corrections.append(("late", a, None, k))
            counts[a] += k
            lines.append(rng.choice([f"A late-sorted vial added {k} more {a}.",
                                     f"Add {k} x {a} from the vial sorted after the tally was typed up."]))
    decoy = rng.choice(present)
    lines.append(rng.choice([f"Checked the {decoy} identifications again: all confirmed.",
                             f"{decoy} numbers look high but the ID is certain; no change."]))

    trap_days = rng.randint(4, 12) if invalid else rng.choice([14, 14, 15, 16, 18, 21])
    if invalid:
        lines.append(rng.choice([f"Trap 2 flooded after a storm; only {trap_days} trap-days of sampling were achieved.",
                                 f"Traps disturbed by cattle -- effective effort {trap_days} trap-days."]))
    else:
        lines.append(f"Sampling effort: {trap_days} trap-days.")

    area = rng.choice([100, 200, 250, 400, 500, 1000, 1250, 2000])
    style = rng.choice(["m2", "ha", "dims"])
    if style == "m2":
        area_text = f"Plot area {area} m^2."
    elif style == "ha":
        area_text = f"Plot area {area / 10000:g} ha."
    else:
        w = rng.choice([d for d in (5, 10, 20, 25, 40, 50) if area % d == 0 and area // d <= 100])
        area_text = f"Plot is {w} m x {area // w} m."
    lines.append(area_text)
    rng.shuffle(lines)
    facts = {"trap_days": trap_days, "corrections": corrections, "area_m2": area}
    tally = "code,count\n" + "".join(f"{c},{k}\n" for c, k in raw)
    notes = f"# {pid} field notes\n\n- Observer: {rng.choice(['R. Hale', 'M. Aydin', 'S. Okoro', 'J. Lind'])}\n\n" + \
        "\n".join(f"- {line}" for line in lines) + "\n"
    return raw, facts, tally, notes


PROTOCOL = f"""# Survey protocol: from tally to diversity

For every plot, in this order:

1. **Synonyms.** Replace every old code in the tally with its current code
   from `species.csv`, and merge the counts.
2. **Corrections.** Apply every correction in the field notes: specimens
   re-identified from one species to another move between them; double counts
   are removed; late-sorted vials are added. A note that only confirms an
   identification changes nothing.
3. **Target group.** Keep ground beetles only (`group` = beetle in
   `species.csv`); drop spiders, ants and unidentified specimens (UNK).
4. **Effort.** A plot with fewer than {REQUIRED_TRAP_DAYS} trap-days of sampling is **invalid**.
5. **Metrics** over the remaining beetles, where n_i is each species' count and
   N their total:
   - richness: the number of species with n_i > 0;
   - Shannon H' = - sum (n_i/N) ln(n_i/N), natural log;
   - Simpson's index = 1 - sum n_i(n_i - 1) / (N(N - 1));
   - density: N per 100 m^2 of plot area (1 ha = 10,000 m^2).
"""


def species_csv():
    rows = ["code,name,group,current_code"]
    rows += [f"{c},{NAMES[c]},beetle,{c}" for c in BEETLES]
    rows += [f"{old},{NAMES[cur]} (old code),beetle,{cur}" for old, cur in SYNONYMS.items()]
    rows += [f"{c},{NAMES[c]},{g},{c}" for c, g in OTHER.items()]
    return "\n".join(rows) + "\n"


def generate(seed, out=None):
    plan = rng_for(seed, "plan")
    invalid = set(plan.sample(range(N_PLOTS), 9))
    files = {"docs/SURVEY_PROTOCOL.md": PROTOCOL, "species.csv": species_csv()}
    truth = {"seed": seed, "plots": {}}
    for i in range(N_PLOTS):
        pid = f"PL-{i + 1:02d}"
        rng = rng_for(seed, "plot", pid)
        raw, facts, tally, notes = build_plot(rng, pid, i in invalid)
        files[f"plots/{pid}/tally.csv"] = tally
        files[f"plots/{pid}/notes.md"] = notes
        truth["plots"][pid] = dict(analyse(raw, facts), unit_chars=len(tally) + len(notes) + 2500)
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def _close(got, want, abs_tol=None, rel_tol=None):
    try:
        got = float(got)
    except (TypeError, ValueError):
        return False
    return abs(got - want) <= (abs_tol if abs_tol is not None else rel_tol * abs(want))


def grade(seed, answer):
    """Per plot, all or nothing: validity; for a valid plot the exact richness,
    Shannon and Simpson within 0.001, and density within 0.5 %."""
    truth = generate(seed)
    per = {}
    for pid, t in truth["plots"].items():
        got = answer.get(pid) if isinstance(answer.get(pid), dict) else {}
        ok = got.get("valid") is t["valid"]
        if ok and t["valid"]:
            ok = (got.get("richness") == t["richness"] and _close(got.get("shannon"), t["shannon"], abs_tol=0.001)
                  and _close(got.get("simpson"), t["simpson"], abs_tol=0.001)
                  and _close(got.get("density_per_100m2"), t["density_per_100m2"], rel_tol=0.005))
        per[pid] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "plots": per}


def oracle(seed):
    out = {}
    for pid, t in generate(seed)["plots"].items():
        out[pid] = {k: v for k, v in t.items() if k != "unit_chars"}
    return out


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["plots"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(PROTOCOL) + len(species_csv())}


ANSWER_PATH = "/workspace/answer/diversity.json"
INSTRUCTION = """\
# Diversity table for the ground-beetle survey

The season's pitfall-trap results are in `/workspace/plots/`: one folder per
plot with the tally and the observer's field notes. Turn every plot into its
row of the diversity table, following `docs/SURVEY_PROTOCOL.md` and the
checklist in `species.csv`.

Write `/workspace/answer/diversity.json`:

```json
{"PL-NN": {"valid": true, "richness": 0, "shannon": 0.0, "simpson": 0.0, "density_per_100m2": 0.0},
 "PL-MM": {"valid": false}}
```
"""

META = {
    "unit": "plot", "kind": "diversity indices", "domain": "field ecology",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "a fixed procedure applied to data that each observer's notes quietly amend",
    "deliverable": "`/workspace/answer/diversity.json`",
    "grading": "Per plot, all or nothing: validity; exact richness; Shannon and Simpson within 0.001; density "
               "within 0.5 %. Reward is the mean.",
    "per_unit": "merge synonym codes, apply the notes' re-identifications, double counts and late vials, drop "
                "spiders, ants and unidentified specimens, check the sampling effort, and compute the four metrics",
    "traps": [
        "**Synonym codes** split one species' count across two rows.",
        "**Re-identifications** move individuals between species; a confirmation note changes nothing.",
        "**Non-target taxa** (spiders, ants, UNK) sit in the same tally.",
        "**Area** in m^2, hectares, or as length x width.",
        "**Natural log** for Shannon; Simpson with n(n-1), not p^2.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
