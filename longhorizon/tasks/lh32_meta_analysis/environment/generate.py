#!/usr/bin/env python3
"""LH32 -- screen 56 trial reports for a meta-analysis and pool the included trials.

reports/S-NN.md is one published report of a trial of a structured exercise
programme for adults with depression: its registration number, design,
population, comparator, how many were randomised and completed, and a table of
remission counts at several follow-up weeks. docs/REVIEW_PROTOCOL.md fixes the
review, the same for every report:

- include only randomised trials of adults against placebo or usual care that
  report remission at week 12 ("non-randomised" is not randomised);
- a trial published more than once counts once: the report with more
  participants randomised;
- the effect is the risk ratio of remission, intention to treat -- the number
  RANDOMISED is the denominator, not the number who completed -- from counts or
  from percentages of those randomised;
- zero cells get 0.5 added to every cell;
- the included trials are pooled by fixed-effect inverse-variance weighting.

    python3 lh32_meta_analysis.py --seed 1 --out /fixture
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_REPORTS = 56
SUMMARY_WEIGHT = 0.3
EXCLUSIONS = {"design": 5, "children": 4, "active": 4, "no_week12": 4, "duplicate": 5}
PROGRAMMES = ["supervised aerobic exercise", "group resistance training", "brisk walking programme",
              "yoga-based exercise", "home-based exercise with coaching", "cycling programme"]


# ------------------------------------------------------------------ the protocol

def effect(a, n1, c, n2):
    """log risk ratio and its SE, with 0.5 added to every cell if any is zero."""
    if 0 in (a, n1 - a, c, n2 - c):
        a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1, n2 + 1
    return math.log((a / n1) / (c / n2)), math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)


def pool(effects):
    w = [1 / se ** 2 for _, se in effects]
    y = sum(wi * yi for wi, (yi, _) in zip(w, effects)) / sum(w)
    se = math.sqrt(1 / sum(w))
    return {"k": len(effects), "rr": math.exp(y), "ci_low": math.exp(y - 1.96 * se), "ci_high": math.exp(y + 1.96 * se)}


# ------------------------------------------------------------------ one report

def build(rng, sid, kind, reg, year, n1=None):
    n1 = n1 or rng.randint(30, 160)
    n2 = int(n1 * rng.uniform(0.85, 1.15))
    p_ctrl = rng.uniform(0.08, 0.3)
    rr = rng.uniform(1.1, 2.4)
    a = min(n1, round(n1 * p_ctrl * rr * rng.uniform(0.9, 1.1)))
    c = round(n2 * p_ctrl * rng.uniform(0.9, 1.1))
    if rng.random() < 0.08:
        c = 0  # a small trial where nobody in the control arm remitted
    prog = rng.choice(PROGRAMMES)
    control = rng.choice(["usual care", "placebo (stretching and relaxation sessions)", "usual care"])
    if kind == "active":
        control = rng.choice(["sertraline 50 mg daily", "cognitive behavioural therapy", "escitalopram 10 mg daily"])
    design = rng.choice(["Randomised controlled trial", "Parallel-group randomized trial",
                         "Randomised, assessor-blinded trial"])
    if kind == "design":
        design = rng.choice(["Non-randomised controlled trial", "Prospective observational cohort study",
                             "Controlled before-and-after study (non-randomized)"])
    population = rng.choice(["adults aged 18 to 65 with moderate depression",
                             "adults aged 18-70 with a current major depressive episode",
                             "adults (age 25-60) referred by their GP for low mood"])
    if kind == "children":
        population = rng.choice(["children aged 8 to 12 with depressive symptoms",
                                 "adolescents aged 13-17 with moderate depression"])
    completed1, completed2 = n1 - rng.randint(2, max(3, n1 // 6)), n2 - rng.randint(2, max(3, n2 // 6))
    weeks = [4, 8, 12, 24] if kind != "no_week12" else rng.choice([[4, 8, 24], [6, 16], [8, 26]])
    rows = []
    for wk in weeks:
        if wk == 12:
            ea, ec = a, c
        else:
            f = {4: 0.4, 6: 0.5, 8: 0.7, 16: 1.05, 24: 1.1, 26: 1.1}[wk]
            ea, ec = min(n1, round(a * f)), min(n2, round(c * f))
        style = rng.choice(["count_randomised", "count_completed", "percent"])
        if style == "count_randomised":
            cell = lambda e, n, done: f"{e}/{n}"  # noqa: E731
        elif style == "count_completed":
            cell = lambda e, n, done: f"{e} of {done} completers"  # noqa: E731
        else:
            cell = lambda e, n, done: f"{round(100 * e / n, 1)}%"  # noqa: E731
        rows.append((wk, cell(ea, n1, completed1), cell(ec, n2, completed2)))
    swap = rng.random() < 0.4  # control arm listed first
    head = ("week", control.split(" (")[0], prog) if swap else ("week", prog, control.split(" (")[0])
    lines = [f"# {sid}: {prog.capitalize()} for depression", "",
             f"- Registration: {reg}; published {year}.",
             f"- Design: {design}.",
             f"- Participants: {population}.",
             f"- Comparison: {prog} versus {control}.",
             f"- Randomised: {n1} to {prog}, {n2} to {control.split(' (')[0]}. "
             f"Completed follow-up: {completed1} and {completed2}.",
             "", "Remission (percentages are of those randomised to each arm):", "",
             f"| {' | '.join(head)} |", "|---|---|---|"]
    for wk, x, y in rows:
        lines.append(f"| {wk} | {y if swap else x} | {x if swap else y} |")
    return "\n".join(lines) + "\n", {"n1": n1, "n2": n2, "a": a, "c": c}


PROTOCOL = """# Review protocol

Question: does a structured exercise programme increase remission of
depression in adults, compared with placebo or usual care?

1. **Include** a report only if it is a randomised trial ("randomised" or
   "randomized"; a non-randomised or observational study is excluded), of
   adults (aged 18 or over), comparing the exercise programme with placebo or
   usual care (an active comparator such as a drug or a psychotherapy is
   excluded), and reporting remission at week 12.
2. **Duplicates:** reports with the same registration number describe one
   trial. Keep only the report with the most participants randomised
   (if equal, the later year); the others are excluded.
3. **Effect:** risk ratio of remission, exercise versus control, intention to
   treat: the denominators are the numbers RANDOMISED to each arm. Events come
   from the week-12 row: a count ("22/64" or "22 of 55 completers" -- the count
   is 22 either way) or a percentage of those randomised (events = the
   percentage x the number randomised, rounded to the nearest whole number).
4. If any of the four cells (events and non-events in each arm) is zero, add
   0.5 to every cell. log RR = ln((a/n1)/(c/n2)); SE = sqrt(1/a - 1/n1 + 1/c - 1/n2).
5. **Pool** the included trials by fixed-effect inverse-variance weighting
   (weights 1/SE^2) on the log scale; report the pooled RR and its 95% CI
   (pooled log RR +/- 1.96 x sqrt(1 / sum of weights)).
"""


def generate(seed, out=None):
    plan = rng_for(seed, "plan")
    kinds = sum(([k] * n for k, n in EXCLUSIONS.items()), [])
    kinds += ["include"] * (N_REPORTS - len(kinds))
    plan.shuffle(kinds)
    ids = [f"S-{i + 1:02d}" for i in range(N_REPORTS)]
    regs = {sid: f"ISRCTN{plan.randint(10000000, 99999999)}" for sid in ids}
    # each duplicate is a second report of an included trial: same registration, fewer randomised
    included = [s for s, k in zip(ids, kinds) if k == "include"]
    dup_of = {}
    for sid, k in zip(ids, kinds):
        if k == "duplicate":
            dup_of[sid] = plan.choice([s for s in included if s not in dup_of.values()])
            regs[sid] = regs[dup_of[sid]]
    files = {"docs/REVIEW_PROTOCOL.md": PROTOCOL}
    truth = {"seed": seed, "studies": {}}
    effects, sizes = [], {}
    # full reports first, so each duplicate (an interim report) can be smaller than its trial's
    for sid, kind in sorted(zip(ids, kinds), key=lambda x: x[1] == "duplicate"):
        rng = rng_for(seed, "report", sid)
        year = rng.randint(2012, 2024)
        n1 = max(12, int(sizes[dup_of[sid]] * 0.6)) if kind == "duplicate" else None
        text, f = build(rng, sid, kind if kind != "duplicate" else "include", regs[sid], year, n1=n1)
        sizes[sid] = f["n1"]
        files[f"reports/{sid}.md"] = text
        if kind == "include":
            y, se = effect(f["a"], f["n1"], f["c"], f["n2"])
            truth["studies"][sid] = {"include": True, "log_rr": y, "se": se}
            effects.append((y, se))
        else:
            truth["studies"][sid] = {"include": False, "reason": kind}
        truth["studies"][sid]["unit_chars"] = len(text) + 2500
    # a duplicate (interim, smaller) report must have fewer randomised than its full report
    for d, full in dup_of.items():
        nd = sum(map(int, _randomised(files[f"reports/{d}.md"])))
        nf = sum(map(int, _randomised(files[f"reports/{full}.md"])))
        assert nd < nf, (d, full)
    truth["studies"] = {sid: truth["studies"][sid] for sid in ids}
    truth["pooled"] = pool(effects)
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def _randomised(text):
    import re
    m = re.search(r"Randomised: (\d+) to .*?, (\d+) to", text)
    return m.group(1), m.group(2)


def _close(got, want, abs_tol=None, rel_tol=None):
    try:
        got = float(got)
    except (TypeError, ValueError):
        return False
    return abs(got - want) <= (abs_tol if abs_tol is not None else rel_tol * abs(want))


def grade(seed, answer):
    """Per report: the include decision, and for an included trial log RR within
    0.005 and SE within 1 %. Pooled: k exactly, RR and CI within 0.5 %.
    Reward = 0.7 x report accuracy + 0.3 x pooled."""
    truth = generate(seed)
    studies = answer.get("studies") if isinstance(answer.get("studies"), dict) else {}
    per = {}
    for sid, t in truth["studies"].items():
        got = studies.get(sid) if isinstance(studies.get(sid), dict) else {}
        ok = got.get("include") is t["include"]
        if ok and t["include"]:
            ok = _close(got.get("log_rr"), t["log_rr"], abs_tol=0.005) and _close(got.get("se"), t["se"], rel_tol=0.01)
        per[sid] = float(ok)
    p, tp = answer.get("pooled") if isinstance(answer.get("pooled"), dict) else {}, truth["pooled"]
    pooled_ok = p.get("k") == tp["k"] and all(_close(p.get(k), tp[k], rel_tol=0.005) for k in ("rr", "ci_low", "ci_high"))
    acc = sum(per.values()) / len(per)
    return {"reward": round((1 - SUMMARY_WEIGHT) * acc + SUMMARY_WEIGHT * pooled_ok, 4),
            "report_accuracy": round(acc, 4), "pooled_correct": pooled_ok, "studies": per}


def oracle(seed):
    t = generate(seed)
    studies = {sid: ({"include": True, "log_rr": s["log_rr"], "se": s["se"]} if s["include"] else {"include": False})
               for sid, s in t["studies"].items()}
    return {"studies": studies, "pooled": t["pooled"]}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [s["unit_chars"] for s in t["studies"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(PROTOCOL) + 300}


ANSWER_PATH = "/workspace/answer/review.json"
INSTRUCTION = """\
# Systematic review: exercise for depression

The search produced the trial reports in `/workspace/reports/`. Screen and
extract every report by `docs/REVIEW_PROTOCOL.md`, then pool the included
trials.

Write `/workspace/answer/review.json`:

```json
{"studies": {"S-NN": {"include": true, "log_rr": 0.0, "se": 0.0},
             "S-MM": {"include": false, "reason": "..."}},
 "pooled": {"k": 0, "rr": 0.0, "ci_low": 0.0, "ci_high": 0.0}}
```
"""

META = {
    "unit": "trial report", "kind": "evidence synthesis", "domain": "clinical trials",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "eligibility judgements and extraction per report, then a pooled estimate only right if every "
                    "report's decision is",
    "deliverable": "`/workspace/answer/review.json`",
    "grading": "Per report: the include decision, and for an included trial log RR within 0.005 and SE within 1 %. "
               "Pooled: k, RR and CI. Reward = 0.7 x report accuracy + 0.3 x pooled.",
    "per_unit": "check design, population, comparator and the week-12 outcome, match the registration number "
                "against other reports, read events from the week-12 row, use the randomised denominators, and "
                "compute log RR and SE",
    "traps": [
        "**\"Non-randomised\"** contains \"randomised\".",
        "**Duplicates** share a registration number; keep the report with more randomised.",
        "**Intention to treat**: the denominator is randomised, not completers.",
        "**Percentages** of those randomised must be turned back into counts.",
        "**Arm order** varies; **zero cells** need the 0.5 correction.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
