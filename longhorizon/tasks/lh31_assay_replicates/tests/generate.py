#!/usr/bin/env python3
"""LH31 -- analyse 56 replicate runs of the same assay, then report their average.

Every run under runs/R-NN/ is the SAME procedure -- a plate-reader assay of one
sample against a calibration curve, docs/PROTOCOL.md -- repeated on a different
day, and no two runs are alike:

- a different reader (instruments.csv), whose linear range decides which
  standards the fit may use;
- standards recorded in different units (mg/L, ug/mL, mg/dL, umol/L with the
  analyte's molar mass);
- the dilution written differently ("1:20", "1 in 20", "20-fold",
  "50 uL sample + 950 uL buffer" -- which is 20, not 19);
- wells the operator excluded, in prose, next to wells mentioned but kept;
- and some runs must not be reported at all: a calibration that fails QC,
  too few usable standards, a contaminated sample, or a run superseded by a
  later repeat -- which only the LATER run's notes say.

The deliverable is each replicate's verdict and concentration, then the mean
and standard deviation over the valid ones: the average is only right if every
replicate's validity is.

    python3 lh31_assay_replicates.py --seed 1 --out /fixture
"""

import csv
import io
import json
import math
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_RUNS = 56
DESIGN = {"valid": 40, "noisy": 4, "too_few": 4, "contaminated": 4, "superseded": 4}
INSTRUMENTS = {"PR-100": 1.8, "PR-220": 2.2, "SX-9": 2.6}   # max corrected absorbance in the linear range
LEVELS_MG_L = [0.5, 1, 2, 4, 8, 12, 16]
MW = {"glucose": 180.16, "lactate": 90.08, "urea": 60.06}
ROWS = "ABCDEFGH"
REL_TOL = 0.005      # concentrations and the mean: 0.5 %
SD_REL_TOL = 0.03    # standard deviation: 3 %
SUMMARY_WEIGHT = 0.3


# ------------------------------------------------------------------ the protocol

def fit(xs, ys):
    """Ordinary least squares y = m x + b, and R^2."""
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    m = sxy / sxx
    b = my - m * mx
    ss_res = sum((y - (m * x + b)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return m, b, 1 - ss_res / ss_tot


def unit_factor(unit, analyte):
    return {"mg/L": 1.0, "ug/mL": 1.0, "mg/dL": 10.0}.get(unit) or MW[analyte] / 1000.0


def analyse(rows, facts):
    """docs/PROTOCOL.md, exactly: the reference every replicate is graded against."""
    if facts["not_reportable"]:
        return {"valid": False, "reason": "not reportable"}
    if facts["superseded_by"]:
        return {"valid": False, "reason": f"superseded by {facts['superseded_by']}"}
    wells = [r for r in rows if r["well"] not in facts["excluded"]]
    blank = statistics.fmean(float(r["absorbance"]) for r in wells if r["type"] == "blank")
    k = unit_factor(facts["unit"], facts["analyte"])
    std = [(float(r["conc"]) * k, float(r["absorbance"]) - blank) for r in wells if r["type"] == "standard"]
    std = [(c, a) for c, a in std if a <= INSTRUMENTS[facts["instrument"]]]
    if len(std) < 4:
        return {"valid": False, "reason": f"only {len(std)} standards in range"}
    m, b, r2 = fit([c for c, _ in std], [a for _, a in std])
    if r2 < 0.99:
        return {"valid": False, "reason": f"calibration R^2 {r2:.4f} < 0.99"}
    sample = statistics.fmean(float(r["absorbance"]) - blank for r in wells if r["type"] == "sample")
    return {"valid": True, "conc_mg_l": (sample - b) / m * facts["dilution"], "r2": r2}


PROTOCOL = """# Assay protocol: analysing one run

Each run is one plate: blank wells, one well per calibration standard, and the
sample in triplicate, read on the instrument named in the run's notes. The
sample was diluted before plating; report the concentration in the ORIGINAL
sample, in mg/L.

1. **Exclusions.** Drop every well the operator's notes say to exclude
   (bubbles, pipetting errors, and so on). A well the notes mention but keep is
   kept.
2. **Blank.** Subtract the mean of the remaining blank wells from every
   remaining well ("corrected absorbance").
3. **Standards.** Convert each standard's concentration to mg/L:
   mg/L and ug/mL are the same; mg/dL x 10; umol/L x (molar mass in g/mol) / 1000.
   Drop every standard whose corrected absorbance is ABOVE the reader's linear
   limit in `instruments.csv`.
4. **Calibration.** Fit corrected absorbance = slope x concentration + intercept
   by ordinary least squares over the remaining standards.
5. **QC.** The run is **invalid** if fewer than 4 standards remain, or if the
   fit's R^2 is below 0.99.
6. **Sample.** concentration = (mean corrected sample absorbance - intercept) /
   slope x dilution factor.
   Dilutions are written several ways, all meaning the same total factor N:
   "1:N", "1 in N", "N-fold", "dilution factor N". "A uL sample + B uL diluent"
   is a factor of (A + B) / A. "Undiluted" is 1.
7. **Not reportable.** A run is also invalid if its notes say the sample was
   compromised, or if a LATER run's notes say it repeats this run -- the repeat
   replaces it.

## Summary

Over the valid runs only: their number, the mean concentration, and the
sample standard deviation (n - 1).
"""


# ------------------------------------------------------------------ one replicate

def dilution_text(rng, d):
    a = rng.choice([25, 50, 100])
    return rng.choice([f"Sample diluted 1:{d} in assay buffer.", f"Diluted 1 in {d} before plating.",
                       f"{d}-fold dilution in buffer.", f"Dilution factor {d}.",
                       f"{a} uL sample + {a * (d - 1)} uL buffer."])


def exclusion_text(rng, wells):
    if not wells:
        return []
    verb, noun = rng.choice([("had bubbles", "bubbles"), ("had a pipetting error", "pipetting error"),
                             ("sits on a scratch in the plate", "scratched plate"),
                             ("was touched by the tip", "tip contact")])
    if len(wells) == 1:
        return [rng.choice([f"Well {wells[0]} {verb} -- exclude it.", f"Exclude {wells[0]} ({noun}).",
                            f"Drop well {wells[0]}: it {verb}."])]
    return [f"Wells {wells[0]} and {wells[1]}: {noun}. Exclude both."]


def build_run(rng, kind, true_conc, analyte):
    """Draw one run of `kind` until the protocol agrees it is that kind."""
    for _attempt in range(400):
        instrument = rng.choice(list(INSTRUMENTS))
        unit = rng.choice(["mg/L", "ug/mL", "mg/dL", "umol/L"])
        dilution = rng.choice([5, 8, 10, 16, 20])
        slope, intercept, blank = rng.uniform(0.10, 0.17), rng.uniform(-0.01, 0.03), rng.uniform(0.04, 0.09)
        levels = LEVELS_MG_L[:5] + [16] if kind == "too_few" else LEVELS_MG_L
        noise = 0.07 if kind == "noisy" else 0.004
        k = unit_factor(unit, analyte)
        limit = INSTRUMENTS[instrument]
        rows, n = [], 0

        def well():
            nonlocal n
            n += 1
            return f"{ROWS[(n - 1) // 12]}{(n - 1) % 12 + 1}"

        for _ in range(rng.randint(2, 4)):
            rows.append({"well": well(), "type": "blank", "conc": "", "absorbance": blank + rng.gauss(0, 0.003)})
        for c in levels:
            a = intercept + slope * c + rng.gauss(0, noise)
            if a > limit:  # the reader saturates above its linear range
                a = limit + 0.35 * (a - limit)
            conc = round(c / k, 2 if unit == "umol/L" else 3)
            rows.append({"well": well(), "type": "standard", "conc": f"{conc:g}", "absorbance": blank + a})
        diluted = true_conc / dilution
        for _ in range(3):
            rows.append({"well": well(), "type": "sample", "conc": "",
                         "absorbance": blank + intercept + slope * diluted + rng.gauss(0, 0.005)})
        for r in rows:
            r["absorbance"] = f"{r['absorbance']:.4f}"

        # Exclusions: corrupt the wells the operator flagged, so ignoring the notes costs.
        n_excl = 2 if kind == "too_few" else rng.choice([0, 1, 1, 2])
        pool = [r for r in rows if r["type"] == "standard"] if kind == "too_few" else rows
        excluded = sorted(r["well"] for r in rng.sample(pool, n_excl))
        left = [r["type"] for r in rows if r["well"] not in excluded]
        if left.count("blank") < 1 or left.count("sample") < 2:
            continue
        for r in rows:
            if r["well"] in excluded:
                r["absorbance"] = f"{float(r['absorbance']) + rng.uniform(0.25, 0.6):.4f}"
        kept = rng.choice([r["well"] for r in rows if r["well"] not in excluded])

        facts = {"instrument": instrument, "unit": unit, "analyte": analyte, "dilution": dilution,
                 "excluded": excluded, "not_reportable": kind == "contaminated", "superseded_by": None,
                 "kept_mention": kept}
        # Parse back what we will write, so the truth is computed from the file's own numbers.
        text = to_csv(rows)
        parsed = list(csv.DictReader(io.StringIO(text)))
        got = analyse(parsed, dict(facts, not_reportable=False))
        saturated = any(float(r["absorbance"]) - statistics.fmean(
            float(x["absorbance"]) for x in parsed if x["type"] == "blank" and x["well"] not in excluded) > limit
            for r in parsed if r["type"] == "standard" and r["well"] not in excluded)
        traps = bool(excluded) + (unit != "mg/L") + saturated
        if kind in ("valid", "superseded", "contaminated"):
            ok = got["valid"] and got["r2"] >= 0.995 and traps >= 1
        elif kind == "noisy":
            ok = not got["valid"] and "R^2" in got["reason"] and _r2(parsed, facts) < 0.985
        else:
            ok = not got["valid"] and "standards" in got["reason"]
        if ok:
            return text, facts
    raise RuntimeError(f"could not realise a {kind} run")


def _r2(rows, facts):
    wells = [r for r in rows if r["well"] not in facts["excluded"]]
    blank = statistics.fmean(float(r["absorbance"]) for r in wells if r["type"] == "blank")
    k = unit_factor(facts["unit"], facts["analyte"])
    std = [(float(r["conc"]) * k, float(r["absorbance"]) - blank) for r in wells if r["type"] == "standard"]
    std = [(c, a) for c, a in std if a <= INSTRUMENTS[facts["instrument"]]]
    return fit([c for c, _ in std], [a for _, a in std])[2]


def to_csv(rows):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=["well", "type", "conc", "absorbance"], lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


def notes_md(rng, rid, facts, repeats):
    unit = facts["unit"]
    unit_line = (f"Standards are in {unit}." if unit != "umol/L" else
                 f"Standards are in umol/L ({facts['analyte']}, molar mass {MW[facts['analyte']]} g/mol).")
    lines = [f"# {rid} operator notes", "",
             f"- Reader: {facts['instrument']}",
             f"- Operator: {rng.choice(['A. Okafor', 'L. Brandt', 'M. Silva', 'J. Kowalski', 'R. Tanaka'])}", ""]
    body = [dilution_text(rng, facts["dilution"]), unit_line]
    body += exclusion_text(rng, facts["excluded"])
    body.append(rng.choice([f"Re-checked {facts['kept_mention']}; it reads fine, keep it.",
                            f"{facts['kept_mention']} looked faint but the reading is good.",
                            f"Noted a smudge near {facts['kept_mention']}; wiped, no effect on the reading."]))
    if facts["not_reportable"]:
        body.append(rng.choice(["The sample tube was found uncapped overnight: the sample is compromised and the "
                                "result must not be reported.",
                                "Sample stored at room temperature for 3 days by mistake -- compromised, do not "
                                "report."]))
    if repeats:
        body.append(f"This run repeats {repeats} (reader fault during {repeats}); report this run in its place.")
    body.append(rng.choice(["Plate sealed and read within 10 minutes.", "Room temperature 21 C.",
                            "Buffer lot B-2231.", "Read in endpoint mode at 540 nm."]))
    rng.shuffle(body)
    return "\n".join(lines + body) + "\n"


# ------------------------------------------------------------------ the task

def plan(seed):
    rng = rng_for(seed, "plan")
    kinds = sum(([k] * n for k, n in DESIGN.items()), [])
    rng.shuffle(kinds)
    # A superseded run needs enough valid runs after it to be repeated by one:
    # move any superseded run from the tail to an earlier valid slot.
    while True:
        late = [i for i, k in enumerate(kinds) if k == "superseded"
                and sum(1 for j in range(i + 1, N_RUNS) if kinds[j] == "valid") < DESIGN["superseded"]]
        if not late:
            break
        i = late[-1]
        j = rng.choice([j for j in range(i) if kinds[j] == "valid"])
        kinds[i], kinds[j] = kinds[j], kinds[i]
    ids = [f"R-{i + 1:02d}" for i in range(N_RUNS)]
    # Each superseded run is repeated by a LATER valid run.
    repeats = {}
    later_valid = [i for i, k in enumerate(kinds) if k == "valid"]
    for i, k in enumerate(kinds):
        if k == "superseded":
            cands = [j for j in later_valid if j > i and ids[j] not in repeats]
            repeats[ids[rng.choice(cands)]] = ids[i]
    return ids, kinds, repeats


def generate(seed, out=None):
    ids, kinds, repeats = plan(seed)
    superseded_by = {old: new for new, old in repeats.items()}
    analyte = rng_for(seed, "analyte").choice(list(MW))
    base = rng_for(seed, "base").uniform(35, 60)
    files = {"docs/PROTOCOL.md": PROTOCOL,
             "instruments.csv": "reader,linear_max_corrected_absorbance\n" + "".join(
                 f"{k},{v}\n" for k, v in INSTRUMENTS.items())}
    truth = {"seed": seed, "analyte": analyte, "runs": {}}
    for rid, kind in zip(ids, kinds):
        rng = rng_for(seed, "run", rid)
        true_conc = base * (1 + rng.gauss(0, 0.03))
        text, facts = build_run(rng, kind, true_conc, analyte)
        facts["superseded_by"] = superseded_by.get(rid)
        files[f"runs/{rid}/plate.csv"] = text
        files[f"runs/{rid}/notes.md"] = notes_md(rng, rid, facts, repeats.get(rid))
        result = analyse(list(csv.DictReader(io.StringIO(text))), facts)
        truth["runs"][rid] = {"kind": kind, "valid": result["valid"], "conc_mg_l": result.get("conc_mg_l"),
                              "facts": facts, "unit_chars": len(text) + len(files[f"runs/{rid}/notes.md"]) + 2000}
    valid = [r["conc_mg_l"] for r in truth["runs"].values() if r["valid"]]
    truth["summary"] = {"n_valid": len(valid), "mean_mg_l": statistics.fmean(valid), "sd_mg_l": statistics.stdev(valid)}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def _close(got, want, tol):
    try:
        got = float(got)
    except (TypeError, ValueError):
        return False
    return math.isfinite(got) and abs(got - want) <= tol * abs(want)


def grade(seed, answer):
    """Per replicate: the verdict, and for a valid run the concentration within
    0.5 %. Then the summary: the exact number of valid runs, their mean within
    0.5 % and standard deviation within 3 %. Reward = 0.7 x replicate accuracy
    + 0.3 x summary."""
    truth = generate(seed)
    reps = answer.get("replicates") if isinstance(answer.get("replicates"), dict) else {}
    per = {}
    for rid, t in truth["runs"].items():
        got = reps.get(rid) if isinstance(reps.get(rid), dict) else {}
        ok = got.get("valid") is t["valid"]
        if ok and t["valid"]:
            ok = _close(got.get("conc_mg_l"), t["conc_mg_l"], REL_TOL)
        per[rid] = float(ok)
    s, ts = answer.get("summary") if isinstance(answer.get("summary"), dict) else {}, truth["summary"]
    summary_ok = (s.get("n_valid") == ts["n_valid"] and _close(s.get("mean_mg_l"), ts["mean_mg_l"], REL_TOL)
                  and _close(s.get("sd_mg_l"), ts["sd_mg_l"], SD_REL_TOL))
    acc = sum(per.values()) / len(per)
    return {"reward": round((1 - SUMMARY_WEIGHT) * acc + SUMMARY_WEIGHT * summary_ok, 4),
            "replicate_accuracy": round(acc, 4), "summary_correct": summary_ok, "replicates": per}


def oracle(seed):
    t = generate(seed)
    reps = {rid: ({"valid": True, "conc_mg_l": r["conc_mg_l"]} if r["valid"] else {"valid": False})
            for rid, r in t["runs"].items()}
    return {"replicates": reps, "summary": {k: t["summary"][k] for k in ("n_valid", "mean_mg_l", "sd_mg_l")}}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [r["unit_chars"] for r in t["runs"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(PROTOCOL) + 500}


ANSWER_PATH = "/workspace/answer/replicates.json"
INSTRUCTION = """\
# Replicate assay results for the lab report

The same sample was assayed on many days; each run is in `/workspace/runs/`
(the plate readings and the operator's notes). Analyse every run by
`docs/PROTOCOL.md`, decide which runs are valid, and summarise the valid ones.

Write `/workspace/answer/replicates.json`:

```json
{"replicates": {"R-NN": {"valid": true, "conc_mg_l": 0.0},
                "R-MM": {"valid": false, "reason": "..."}},
 "summary": {"n_valid": 0, "mean_mg_l": 0.0, "sd_mg_l": 0.0}}
```

Concentrations are for the original, undiluted sample, in mg/L.
"""

META = {
    "unit": "replicate run", "kind": "replicate averaging", "domain": "laboratory assays",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "the same procedure repeated on replicates that each differ, then an aggregate that is only "
                    "right if every replicate's verdict is",
    "deliverable": "`/workspace/answer/replicates.json`",
    "grading": "Per replicate: the verdict, and a valid run's concentration within 0.5 %. Summary: the number of "
               "valid runs exactly, their mean within 0.5 % and SD within 3 %. Reward = 0.7 x replicate accuracy "
               "+ 0.3 x summary.",
    "per_unit": "read the run's notes for reader, units, dilution and exclusions, drop excluded wells and "
                "saturated standards, fit the calibration, apply QC, and compute the concentration",
    "traps": [
        "**Every replicate differs**: reader limits, standard units, dilution wording, excluded wells.",
        "**\"50 uL sample + 950 uL buffer\"** is a 20-fold dilution, not 19.",
        "**Saturated standards** above the reader's linear limit bend the fit if kept.",
        "**A superseded run** is named only in the LATER run that repeats it.",
        "**Average only the valid runs**: an invalid one in the mean moves it.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
