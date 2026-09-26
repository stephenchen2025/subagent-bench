#!/usr/bin/env python3
"""LH23 -- audit 50 A/B test write-ups against their data and pre-registration.

experiments/<id>/ holds REPORT.md (what the team claims), PREREG.md (the plan
registered before launch: primary metric, arms, split, minimum sample) and
assignments.csv (one row per user). docs/STANDARDS.md defines the verdict,
checked in this order:

1. exclude users flagged as bots;
2. `srm` -- sample-ratio mismatch: a chi-square test of arm sizes against the
   registered split gives p < 0.001;
3. `underpowered` -- any arm below the registered minimum after exclusions;
4. `wrong_metric` -- the report's headline metric is not the registered primary;
5. `supported` if a two-sided two-proportion z-test on the primary metric gives
   p below 0.05 (Bonferroni-corrected across treatment arms) in the claimed
   direction, else `not_significant`.

Every data set is generated to land on its verdict, and re-checked with the
standards' own statistics before it is written. Traps: bots that push an arm
over the minimum until they are removed; a registered 90/10 split that looks
unbalanced but is not; a three-arm test where p = 0.03 is not enough; a report
whose p-value was computed with bots still in.

    python3 lh23_experiment_audit.py --seed 1 --out /fixture
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_EXPERIMENTS = 50
TRAP_SHARE = 0.7
VERDICTS = {"supported": 15, "not_significant": 13, "srm": 8, "underpowered": 7, "wrong_metric": 7}
METRICS = {"converted": "checkout conversion", "added_to_cart": "add-to-cart rate", "signed_up": "sign-up rate"}


def z_p(x1, n1, x2, n2):
    p = (x1 + x2) / (n1 + n2)
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2)) or 1e-12
    z = (x2 / n2 - x1 / n1) / se
    return math.erfc(abs(z) / math.sqrt(2)), z


def srm_p(counts, split):
    total = sum(counts)
    chi = sum((c - total * s) ** 2 / (total * s) for c, s in zip(counts, split))
    df = len(counts) - 1
    return math.erfc(math.sqrt(chi / 2)) if df == 1 else math.exp(-chi / 2)


def evaluate(rows, prereg, claim_metric):
    """The standards, exactly as docs/STANDARDS.md states them."""
    rows = [r for r in rows if r["is_bot"] == "0"]
    arms = prereg["arms"]
    counts = [sum(1 for r in rows if r["arm"] == a) for a in arms]
    if srm_p(counts, prereg["split"]) < 0.001:
        return "srm"
    if min(counts) < prereg["min_per_arm"]:
        return "underpowered"
    if claim_metric != prereg["metric"]:
        return "wrong_metric"
    m = prereg["metric"]
    ctrl = [r for r in rows if r["arm"] == arms[0]]
    x1, n1 = sum(int(r[m]) for r in ctrl), len(ctrl)
    alpha = 0.05 / (len(arms) - 1)
    best = [r for r in rows if r["arm"] == prereg["claimed_arm"]]
    x2, n2 = sum(int(r[m]) for r in best), len(best)
    p, z = z_p(x1, n1, x2, n2)
    return "supported" if p < alpha and z > 0 else "not_significant"


def naive(rows, prereg, claim_metric):
    """What a hurried analyst computes: bots kept, an even split assumed, one
    uncorrected 0.05 threshold, and the report's metric taken on trust."""
    arms = prereg["arms"]
    counts = [sum(1 for r in rows if r["arm"] == a) for a in arms]
    if srm_p(counts, [1 / len(arms)] * len(arms)) < 0.001:
        return "srm"
    if min(counts) < prereg["min_per_arm"]:
        return "underpowered"
    ctrl = [r for r in rows if r["arm"] == arms[0]]
    best = [r for r in rows if r["arm"] == prereg["claimed_arm"]]
    p, z = z_p(sum(int(r[claim_metric]) for r in ctrl), len(ctrl), sum(int(r[claim_metric]) for r in best), len(best))
    return "supported" if p < 0.05 and z > 0 else "not_significant"


def simulate(rng, verdict, trap=False):
    arms = ["control", "treatment"] if rng.random() < (0.4 if trap else 0.7) else ["control", "treatment_a", "treatment_b"]
    split = ([0.5, 0.5] if len(arms) == 2 and rng.random() < (0.3 if trap else 0.7)
             else [0.9, 0.1] if len(arms) == 2 else [1 / 3] * 3)
    metric = rng.choice(list(METRICS))
    min_per_arm = rng.choice([800, 1000, 1500])
    claimed_arm = arms[-1]
    base = rng.uniform(0.04, 0.12)
    total = int(min_per_arm / min(split) * rng.uniform(1.3, 2.5))
    lift = {"supported": rng.uniform(0.35, 0.6),
            "not_significant": rng.uniform(0.05, 0.3) if trap else rng.uniform(-0.02, 0.06)}.get(verdict, rng.uniform(0.1, 0.3))
    if verdict == "underpowered":
        total = int(min_per_arm / min(split) * rng.uniform(0.6, 0.85))
    eff_split = list(split)
    if verdict == "srm":
        eff_split = [s + (0.03 if i == 0 else -0.03 / (len(split) - 1)) for i, s in enumerate(split)]
        total = int(total * 2)
    rows = []
    uid = 0
    for _ in range(total):
        r = rng.random()
        acc, arm = 0, arms[-1]
        for a, s in zip(arms, eff_split):
            acc += s
            if r < acc:
                arm = a
                break
        rate = base * (1 + lift if arm == claimed_arm else 1)
        uid += 1
        row = {"user_id": str(uid), "arm": arm, "is_bot": "0"}
        for mcol in METRICS:
            row[mcol] = str(int(rng.random() < (rate if mcol == metric else base)))
        rows.append(row)
    # Bots: many, converting at random -- they can push an arm over the minimum.
    for _ in range(int(total * rng.uniform(0.08, 0.3)) if verdict == "underpowered" else int(total * 0.05)):
        uid += 1
        row = {"user_id": str(uid), "arm": rng.choice(arms), "is_bot": "1"}
        for mcol in METRICS:
            row[mcol] = str(int(rng.random() < 0.5))
        rows.append(row)
    rng.shuffle(rows)
    claim_metric = rng.choice([m for m in METRICS if m != metric]) if verdict == "wrong_metric" else metric
    prereg = {"arms": arms, "split": split, "metric": metric, "min_per_arm": min_per_arm, "claimed_arm": claimed_arm}
    return rows, prereg, claim_metric


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    verdicts = sum(([v] * n for v, n in VERDICTS.items()), [])
    rng.shuffle(verdicts)
    files = {"docs/STANDARDS.md": STANDARDS}
    truth = {"seed": seed, "experiments": {}}
    for i, verdict in enumerate(verdicts):
        exp = f"EXP-{2600 + i * 7}"
        erng = rng_for(seed, "exp", exp)
        # Most experiments are built so that the hurried analysis gets them
        # wrong: an uneven registered split, a third arm, bots, a swapped metric.
        trap = verdict != "srm" and erng.random() < TRAP_SHARE  # naive checks catch every SRM too
        for attempt in range(400):
            want_trap = trap and attempt < 300
            rows, prereg, claim = simulate(erng, verdict, want_trap)
            if evaluate(rows, prereg, claim) == verdict and (not want_trap or naive(rows, prereg, claim) != verdict):
                break
        else:
            raise RuntimeError(f"could not realise {verdict} for {exp}")
        split_txt = "/".join(f"{round(s * 100)}" for s in prereg["split"])
        files[f"experiments/{exp}/PREREG.md"] = (
            f"# {exp} pre-registration\n\n- Arms: {', '.join(prereg['arms'])} (control is `{prereg['arms'][0]}`)\n"
            f"- Planned split: {split_txt}\n- Primary metric: {METRICS[prereg['metric']]} (column `{prereg['metric']}`)\n"
            f"- Minimum sample: {prereg['min_per_arm']} users per arm, bots excluded\n")
        claimed_p = round(erng.uniform(0.001, 0.04), 3)
        files[f"experiments/{exp}/REPORT.md"] = (
            f"# {exp} results\n\n**Headline:** `{prereg['claimed_arm']}` improved {METRICS[claim]} "
            f"by {round(erng.uniform(3, 25), 1)}% over control (p = {claimed_p}, significant).\n\n"
            f"We recommend shipping `{prereg['claimed_arm']}`.\n")
        header = ["user_id", "arm", "is_bot"] + list(METRICS)
        files[f"experiments/{exp}/assignments.csv"] = ",".join(header) + "\n" + "".join(
            ",".join(r[h] for h in header) + "\n" for r in rows)
        truth["experiments"][exp] = {"verdict": verdict, "unit_chars": 6000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


STANDARDS = """# Experiment analysis standards

Apply these checks in order; the first that applies is the verdict.

1. Exclude every user with `is_bot = 1`. Everything below uses the rest.
2. **`srm`** -- sample-ratio mismatch. Compute a chi-square goodness-of-fit
   statistic of the arm sizes against the registered split
   (sum over arms of (observed - expected)^2 / expected). With 2 arms the
   p-value is `erfc(sqrt(chi2 / 2))`; with 3 arms it is `exp(-chi2 / 2)`.
   If p < 0.001 the verdict is `srm`.
3. **`underpowered`** -- any arm smaller than the registered minimum.
4. **`wrong_metric`** -- the report's headline metric is not the registered primary metric.
5. Otherwise test the claimed arm against control on the primary metric with a
   two-sided two-proportion z-test (pooled standard error; p = `erfc(|z| / sqrt(2))`).
   The threshold is 0.05 divided by the number of treatment arms. **`supported`**
   if p is below it and the claimed arm is higher; otherwise **`not_significant`**.

Reported p-values are not to be trusted: recompute.
"""


def grade(seed, answer):
    truth = generate(seed)
    per = {e: float(isinstance(answer.get(e), dict) and answer[e].get("verdict") == t["verdict"])
           for e, t in truth["experiments"].items()}
    return {"reward": round(sum(per.values()) / len(per), 4), "experiments": per}


def oracle(seed):
    return {e: {"verdict": t["verdict"]} for e, t in generate(seed)["experiments"].items()}


def solve(seed, path):
    import json
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["experiments"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": len(STANDARDS)}


ANSWER_PATH = "/workspace/answer/verdicts.json"
INSTRUCTION = """\
# Experiment review board

Every experiment under `/workspace/experiments/` wants to ship. Before the
review board meets, check each write-up against its pre-registration and its
data, following `docs/STANDARDS.md` exactly.

Write `/workspace/answer/verdicts.json`:

```json
{"EXP-NNNN": {"verdict": "supported" | "not_significant" | "srm" | "underpowered" | "wrong_metric"}}
```
"""

META = {
    "unit": "experiment", "kind": "statistical verdicts", "domain": "A/B experiments", "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "statistical judgement under a fixed protocol, where the write-up is not to be trusted",
    "deliverable": "`/workspace/answer/verdicts.json`",
    "grading": "Per experiment, the verdict. Reward is the mean.",
    "per_unit": "read the pre-registration and the claim, exclude bots, run the SRM check against the "
                "registered split, check sample sizes, compare metrics, and run the corrected z-test",
    "traps": [
        "**Bots** push arms over the minimum until they are excluded.",
        "**A 90/10 split** is unbalanced by design; testing it against 50/50 finds a false SRM.",
        "**Three arms** halve the threshold.",
        "**Reported p-values** are always under 0.05; recompute.",
        "**Check order matters**: an SRM experiment is `srm` even if its metric is also wrong.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
