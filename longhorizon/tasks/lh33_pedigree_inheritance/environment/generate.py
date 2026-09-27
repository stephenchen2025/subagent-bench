#!/usr/bin/env python3
"""LH33 -- decide which inheritance modes each of 50 family pedigrees allows.

families/F-NN.md is a clinic's record of one family: every member's sex,
parents and phenotype (affected, unaffected, or not examined), with notes such
as "married into the family" or "adopted". docs/INHERITANCE.md fixes the
reasoning rules: full penetrance, no new mutations, a rare allele -- so an
unaffected person who married into the family carries none -- and five modes
to test: autosomal dominant (AD), autosomal recessive (AR), X-linked dominant
(XLD), X-linked recessive (XLR) and mitochondrial (MT).

For each family the answer is the exact SET of modes that can explain every
phenotype. Each pedigree is its own proof: which transmissions each mode
forbids, through carriers nobody examined, around an adoptee whose listed
parents are not biological, and across spouses who cannot be carriers.

    python3 lh33_pedigree_inheritance.py --seed 1 --out /fixture
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_FAMILIES = 50
MODES = ["AD", "AR", "XLD", "XLR", "MT"]
ROMAN = ["I", "II", "III", "IV"]
FIRST = {"M": ["Arno", "Bram", "Cas", "Dirk", "Emil", "Floris", "Gijs", "Hugo", "Ivo", "Jens", "Koen", "Lars",
               "Milan", "Niels", "Otto", "Pim", "Rens", "Sem", "Tijn", "Wout"],
         "F": ["Anouk", "Bente", "Cato", "Dewi", "Elin", "Fenna", "Guusje", "Hanna", "Isa", "Jente", "Kiki",
               "Lotte", "Maud", "Noor", "Olga", "Puck", "Roos", "Saar", "Tess", "Vera"]}


# ------------------------------------------------------------------ genetics

def genotypes(mode, sex):
    """Possible genotypes: copies of the disease allele (MT: 0/1 for the mitochondria)."""
    if mode == "MT":
        return (0, 1)
    if mode in ("XLD", "XLR") and sex == "M":
        return (0, 1)
    return (0, 1, 2)


def affected(mode, sex, g):
    if mode in ("AD", "XLD", "MT"):
        return g >= 1
    if mode == "AR":
        return g == 2
    return g == 1 if sex == "M" else g == 2  # XLR


def transmits(g):
    return {0: (0,), 1: (0, 1), 2: (1,)}[g]


def child_options(mode, sex, gf, gm):
    """Child genotypes possible from a father with gf and a mother with gm."""
    if mode == "MT":
        return {gm}
    if mode in ("XLD", "XLR"):
        if sex == "M":
            return set(transmits(gm))          # a son's X comes from his mother
        return {gf + b for b in transmits(gm)}  # a daughter gets her father's only X
    return {a + b for a in transmits(gf) for b in transmits(gm)}


def consistent(mode, people):
    """Is there a genotype for everyone that obeys Mendel and every phenotype?

    people: id -> {sex, father, mother, status, founder_kind}. The two founders
    at the top ("original") may carry anything their phenotype allows; an
    unaffected spouse who married in, and an adoptee ("outside"), carry nothing
    (rare allele); an affected one carries whatever makes them affected.

    Arc consistency over nuclear families. Nobody here marries a relative, so
    the families form a tree and a fixpoint with no empty domain is exact.
    """
    dom = {}
    for pid, p in people.items():
        gs = {g for g in genotypes(mode, p["sex"])
              if p["status"] == "not examined" or affected(mode, p["sex"], g) == (p["status"] == "affected")}
        if p["founder_kind"] == "outside" and p["status"] != "affected":
            gs &= {0}
        dom[pid] = gs
    families = {}
    for pid, p in people.items():
        if p["father"] and p["mother"]:
            families.setdefault((p["father"], p["mother"]), []).append(pid)
    changed = True
    while changed:
        changed = False
        for (f, m), kids in families.items():
            pairs = [(gf, gm) for gf in dom[f] for gm in dom[m]
                     if all(dom[k] & child_options(mode, people[k]["sex"], gf, gm) for k in kids)]
            new = {f: {a for a, _ in pairs}, m: {b for _, b in pairs}}
            for k in kids:
                new[k] = dom[k] & set().union(*(child_options(mode, people[k]["sex"], a, b) for a, b in pairs)) \
                    if pairs else set()
            for pid, gs in new.items():
                if gs != dom[pid]:
                    dom[pid] = gs
                    changed = True
            if any(not dom[x] for x in new):
                return False
    return all(dom.values())


def modes_allowed(people):
    return [m for m in MODES if consistent(m, people)]


# ------------------------------------------------------------------ one family

def simulate(rng, mode):
    """Draw a three- or four-generation family whose disease follows `mode`."""
    people, records = {}, []
    names = {"M": list(FIRST["M"]), "F": list(FIRST["F"])}
    rng.shuffle(names["M"])
    rng.shuffle(names["F"])
    counters = [0, 0, 0, 0]

    def new(gen, sex, father, mother, g, kind, note=""):
        counters[gen] += 1
        pid = f"{ROMAN[gen]}-{counters[gen]}"
        people[pid] = {"sex": sex, "father": father, "mother": mother, "g": g, "founder_kind": kind, "note": note,
                       "name": names[sex].pop() if names[sex] else f"{sex}{len(people)}"}
        return pid

    def founder_g(sex, carrier):
        if not carrier:
            return 0
        opts = [g for g in genotypes(mode, sex) if g > 0]
        # keep carriers mostly heterozygous so recessive modes skip generations
        return 1 if 1 in opts and rng.random() < 0.85 else opts[-1]

    # Generation I: the original couple; the disease allele enters through one or both.
    carrier_side = rng.choice(["M", "F", "both"])
    if mode == "MT":
        carrier_side = "F"
    if mode == "XLR" and carrier_side == "both":
        carrier_side = "F"
    f1 = new(0, "M", None, None, founder_g("M", carrier_side in ("M", "both")), "original")
    m1 = new(0, "F", None, None, founder_g("F", carrier_side in ("F", "both")), "original")
    generation = [(f1, m1)]
    for gen in range(1, rng.choice([3, 4])):
        next_couples = []
        for father, mother in generation:
            for _ in range(rng.randint(2, 4)):
                sex = rng.choice("MF")
                gf, gm = people[father]["g"], people[mother]["g"]
                if mode == "MT":
                    g = gm
                elif mode in ("XLD", "XLR"):
                    g = rng.choice(transmits(gm)) + (gf if sex == "F" else 0)
                else:
                    g = rng.choice(transmits(gf)) + rng.choice(transmits(gm))
                child = new(gen, sex, father, mother, g, "child")
                if gen < 3 and rng.random() < 0.6:
                    spouse_sex = "F" if sex == "M" else "M"
                    spouse_affected = rng.random() < 0.08
                    sg = founder_g(spouse_sex, True) if spouse_affected else 0
                    spouse = new(gen, spouse_sex, None, None, sg, "outside", "married into the family")
                    next_couples.append((child, spouse) if sex == "M" else (spouse, child))
            if rng.random() < 0.35:
                # An adoptee: listed with the couple as parents, biologically
                # unrelated -- and half the time affected from their own birth family.
                sex = rng.choice("MF")
                g = max(genotypes(mode, sex)) if rng.random() < 0.5 else 0
                new(gen, sex, father, mother, g, "outside", "adopted")
        generation = next_couples
        if not generation:
            break
    for pid, p in people.items():
        p["status"] = "affected" if affected(mode, p["sex"], p["g"]) else "unaffected"
        if p["founder_kind"] != "outside" and rng.random() < 0.18:
            p["status"] = "not examined"
    return people


def logic_view(people):
    """What the protocol reasons over: adoptees have no biological parents here."""
    view = {}
    for pid, p in people.items():
        adopted = p["note"] == "adopted"
        view[pid] = {"sex": p["sex"], "status": p["status"], "founder_kind": p["founder_kind"],
                     "father": None if adopted else p["father"], "mother": None if adopted else p["mother"]}
    return view


def family_md(fid, people, rng):
    lines = [f"# Family {fid}", "", "| id | name | sex | father | mother | status | notes |",
             "|---|---|---|---|---|---|---|"]
    for pid, p in people.items():
        lines.append(f"| {pid} | {p['name']} | {p['sex']} | {p['father'] or '-'} | {p['mother'] or '-'} | "
                     f"{p['status']} | {p['note']} |")
    lines += ["", rng.choice(["Referred after the proband's diagnosis.", "Family history taken at the genetics clinic.",
                              "Records compiled from two clinic visits."])]
    return "\n".join(lines) + "\n"


RULES = """# Reasoning rules for the pedigree review

For every family, list EVERY mode of inheritance below that can explain all
the recorded phenotypes, under these assumptions:

- **Modes:** AD (autosomal dominant), AR (autosomal recessive), XLD (X-linked
  dominant), XLR (X-linked recessive), MT (mitochondrial: passed only from a
  mother to all of her children; everyone who carries it is affected).
- **Full penetrance:** a person with the disease genotype is affected; no new
  mutations.
- **Rare allele:** a person who **married into the family** and is unaffected
  carries no disease allele. The two founders at the top of the family may
  carry anything their phenotype allows.
- **Adopted** members are not biologically related to the parents listed for
  them; treat them like someone who married in.
- **Not examined** members may have either phenotype.
- A mode is allowed if SOME assignment of genotypes to everyone obeys Mendelian
  transmission and every recorded phenotype. List all allowed modes, in the
  order AD, AR, XLD, XLR, MT. If none fits, give an empty list.
"""


def generate(seed, out=None):
    files = {"docs/INHERITANCE.md": RULES}
    truth = {"seed": seed, "families": {}}
    plan = rng_for(seed, "plan")
    for i in range(N_FAMILIES):
        fid = f"F-{i + 1:02d}"
        rng = rng_for(seed, "family", fid)
        mode = plan.choice(MODES)
        for _ in range(200):
            people = simulate(rng, mode)
            n_aff = sum(p["status"] == "affected" for p in people.values())
            allowed = modes_allowed(logic_view(people))
            # enough evidence to rule something out, and the true mode must survive
            if n_aff >= 3 and mode in allowed and len(allowed) <= 3 and 14 <= len(people) <= 30:
                break
        else:
            raise RuntimeError(f"could not draw {fid}")
        files[f"families/{fid}.md"] = family_md(fid, people, rng)
        truth["families"][fid] = {"modes": allowed, "true_mode": mode,
                                  "unit_chars": len(files[f"families/{fid}.md"]) + 2500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def grade(seed, answer):
    """Per family, all or nothing: exactly the set of allowed modes."""
    truth = generate(seed)
    per = {}
    for fid, t in truth["families"].items():
        got = answer.get(fid)
        got = got.get("modes") if isinstance(got, dict) else got
        per[fid] = float(isinstance(got, list) and sorted(set(map(str, got))) == sorted(t["modes"]))
    return {"reward": round(sum(per.values()) / len(per), 4), "families": per}


def oracle(seed):
    return {fid: {"modes": t["modes"]} for fid, t in generate(seed)["families"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["families"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(RULES) + 500}


ANSWER_PATH = "/workspace/answer/modes.json"
INSTRUCTION = """\
# Pedigree review for the genetics clinic

Each file in `/workspace/families/` is one referred family. For every family,
work out which modes of inheritance are compatible with all of its recorded
phenotypes, following the assumptions in `docs/INHERITANCE.md`.

Write `/workspace/answer/modes.json`:

```json
{"F-NN": {"modes": ["AD", "XLD"]}}
```
"""

META = {
    "unit": "family", "kind": "inheritance inference", "domain": "human genetics",
    "output_tokens": 1600, "needs_pytest": False,
    "failure_mode": "a proof per unit: which transmissions each mode forbids, through unexamined carriers",
    "deliverable": "`/workspace/answer/modes.json`",
    "grading": "Per family, all or nothing: exactly the set of modes the pedigree allows. Reward is the mean.",
    "per_unit": "for each of five modes, try to assign genotypes that fit every phenotype: follow sons' X from "
                "their mothers, carriers through unexamined members, and the non-carrier spouses",
    "traps": [
        "**Married-in spouses** who are unaffected carry nothing, which rules out AR in many families.",
        "**Adoptees** are listed with parents who are not biological.",
        "**Not examined** members can be carriers or affected.",
        "**X-linked**: a son's X comes from his mother; an affected father passes XLD to every daughter.",
        "**Textbook heuristics** (\"skips a generation, so recessive\") pick one mode; the answer is the full set.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
