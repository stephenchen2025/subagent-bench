#!/usr/bin/env python3
"""LH38 -- solve 56 counting and probability problems, exactly.

problems/Q-NN.md is one word problem from a combinatorics problem set. The
answer is an exact integer or fraction in lowest terms (docs/ANSWERS.md). No
two problems are the same: eight kinds, each with its own numbers and a twist
that changes the count -- a round table instead of a row, repeated letters,
"at least" instead of "exactly", bounds on the variables, a blocked corner on
a grid, drawing with or without replacement, a pair who refuse to sit
together.

Every answer is computed by brute-force enumeration, never by formula, so the
ground truth does not depend on the reasoning the task is testing.

    python3 lh38_counting_problems.py --seed 1 --out /fixture
"""

import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_PROBLEMS = 56
WORDS = ["BANANA", "LETTER", "COOKIE", "PEPPER", "BALLOT", "SEESAW", "TOFFEE", "COFFEE", "MAMMAL", "PUZZLE",
         "BOOKKEEP", "ASSESS", "RIPPLE", "CANNON", "GAGGLE"]
NAMES = ["Ana", "Ben", "Cai", "Dev", "Eli", "Fay", "Gus", "Hal", "Ida", "Jo"]


def fmt(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


# ------------------------------------------------------------------ problem kinds

def letters(rng):
    w = rng.choice(WORDS)
    rule = rng.choice(["none", "no_adjacent_same", "vowels_together", "starts_ends_same"])
    perms = set(itertools.permutations(w))
    if rule == "no_adjacent_same":
        perms = {p for p in perms if all(p[i] != p[i + 1] for i in range(len(p) - 1))}
        text = f"How many distinct arrangements of the letters of {w} have no two identical letters next to each other?"
    elif rule == "vowels_together":
        vow = set("AEIOU")
        perms = {p for p in perms if (lambda idx: max(idx) - min(idx) == len(idx) - 1)(
            [i for i, ch in enumerate(p) if ch in vow])}
        text = f"How many distinct arrangements of the letters of {w} keep all the vowels in one consecutive block?"
    elif rule == "starts_ends_same":
        perms = {p for p in perms if p[0] == p[-1]}
        text = f"How many distinct arrangements of the letters of {w} begin and end with the same letter?"
    else:
        text = f"How many distinct arrangements are there of the letters of the word {w}?"
    return text, len(perms)


def dice(rng):
    k, n = rng.choice([(2, 6), (3, 6), (3, 4), (2, 8), (4, 4), (3, 8), (2, 12), (4, 6)])
    s = rng.randint(k + 2, k * n - 2)
    cmp = rng.choice(["exactly", "at least", "at most"])
    outcomes = list(itertools.product(range(1, n + 1), repeat=k))
    ok = sum(1 for o in outcomes if (sum(o) == s if cmp == "exactly" else sum(o) >= s if cmp == "at least" else sum(o) <= s))
    text = f"{k} fair {n}-sided dice (faces 1 to {n}) are rolled. What is the probability that the total is {cmp} {s}?"
    return text, Fraction(ok, len(outcomes))


def committee(rng):
    men, women = rng.randint(4, 7), rng.randint(4, 7)
    size = rng.randint(3, 5)
    at_least = rng.randint(1, min(size - 1, women))
    feud = rng.random() < 0.6
    people = [("M", i) for i in range(men)] + [("W", i) for i in range(women)]
    count = 0
    for c in itertools.combinations(people, size):
        if sum(1 for p in c if p[0] == "W") < at_least:
            continue
        if feud and ("M", 0) in c and ("W", 0) in c:
            continue
        count += 1
    text = (f"A club has {men} men and {women} women. How many committees of {size} can be formed with at least "
            f"{at_least} {'woman' if at_least == 1 else 'women'}")
    text += (", if one particular man and one particular woman refuse to serve together?" if feud else "?")
    return text, count


def bounded_sum(rng):
    k = rng.randint(3, 4)
    n = rng.randint(8, 14)
    lows = [rng.choice([0, 0, 1, 2]) for _ in range(k)]
    highs = [rng.choice([None, None, rng.randint(3, 6)]) for _ in range(k)]
    count = 0
    for xs in itertools.product(range(n + 1), repeat=k):
        if sum(xs) == n and all(x >= lo for x, lo in zip(xs, lows)) and all(h is None or x <= h for x, h in zip(xs, highs)):
            count += 1
    conds = []
    for i, (lo, h) in enumerate(zip(lows, highs), 1):
        if h is not None:
            conds.append(f"{lo} <= x{i} <= {h}")
        else:
            conds.append(f"x{i} >= {lo}")
    text = (f"How many integer solutions does x1 + ... + x{k} = {n} have with " + ", ".join(conds) + "?")
    return text, count


def lattice(rng):
    a, b = rng.randint(4, 7), rng.randint(3, 6)
    rule = rng.choice(["avoid", "through"])
    px, py = rng.randint(1, a - 1), rng.randint(1, b - 1)
    count = 0
    for ups in itertools.combinations(range(a + b), b):  # every path: which of the steps go up
        moves = ["U" if i in ups else "R" for i in range(a + b)]
        x = y = 0
        hit = False
        for mv in moves:
            x, y = (x + 1, y) if mv == "R" else (x, y + 1)
            hit |= (x, y) == (px, py)
        count += (not hit) if rule == "avoid" else hit
    verb = "never pass through" if rule == "avoid" else "pass through"
    text = (f"A path on the grid goes from (0, 0) to ({a}, {b}) using unit steps right or up. How many such paths "
            f"{verb} the point ({px}, {py})?")
    return text, count


def cards(rng):
    ranks, suits = rng.choice([(5, 4), (6, 4), (5, 3), (7, 3)])
    hand = rng.choice([4, 5])
    what = rng.choice(["exactly one pair", "no two cards of the same rank", "at least one card of every suit"])
    deck = list(itertools.product(range(ranks), range(suits)))
    total = ok = 0
    for h in itertools.combinations(deck, hand):
        total += 1
        counts = sorted((sum(1 for c in h if c[0] == r) for r in range(ranks)), reverse=True)
        if what == "exactly one pair":
            ok += counts[0] == 2 and counts[1] < 2
        elif what == "no two cards of the same rank":
            ok += counts[0] == 1
        else:
            ok += len({c[1] for c in h}) == suits
    text = (f"A deck has {ranks} ranks in each of {suits} suits ({ranks * suits} cards). {hand} cards are dealt at random. "
            f"What is the probability that the hand has {what}?")
    return text, Fraction(ok, total)


def seating(rng):
    n = rng.randint(5, 8)
    table = rng.choice(["row", "round"])
    rule = rng.choice(["apart", "together"])
    people = NAMES[:n]
    seen, count = set(), 0
    for p in itertools.permutations(people):
        if table == "round":
            i = p.index(people[0])
            key = p[i:] + p[:i]
            if key in seen:
                continue
            seen.add(key)
            adj = lambda u, v: abs(p.index(u) - p.index(v)) in (1, n - 1)  # noqa: E731
        else:
            adj = lambda u, v: abs(p.index(u) - p.index(v)) == 1  # noqa: E731
        together = adj(people[0], people[1])
        count += together if rule == "together" else not together
    where = ("in a row of chairs" if table == "row" else
             "around a round table (seatings that differ only by rotation are the same)")
    want = "next to each other" if rule == "together" else "not next to each other"
    text = f"{n} people, including {people[0]} and {people[1]}, sit {where}. In how many seatings are {people[0]} and {people[1]} {want}?"
    return text, count


def urn(rng):
    red, blue = rng.randint(3, 7), rng.randint(3, 7)
    draws = rng.randint(3, 4)
    replace = rng.choice([True, False])
    need = rng.randint(1, draws - 1)
    balls = ["R"] * red + ["B"] * blue
    if replace:
        seqs = list(itertools.product(range(len(balls)), repeat=draws))
    else:
        seqs = list(itertools.permutations(range(len(balls)), draws))
    ok = sum(1 for s in seqs if sum(balls[i] == "R" for i in s) >= need)
    how = "with replacement" if replace else "without replacement"
    text = (f"An urn holds {red} red and {blue} blue balls. {draws} balls are drawn one at a time {how}. "
            f"What is the probability that at least {need} of them are red?")
    return text, Fraction(ok, len(seqs))


KINDS = [letters, dice, committee, bounded_sum, lattice, cards, seating, urn]

ANSWERS = """# Answer format

Give every answer exactly: an integer, or a fraction p/q in lowest terms
(for example 5/18). No decimals, no percentages.

Read each problem literally: "at least" includes the bound; arrangements of
letters count identical letters as indistinguishable; seatings around a round
table that differ only by a rotation are the same; "without replacement" means
a drawn ball is not put back.
"""


def generate(seed, out=None):
    files = {"docs/ANSWERS.md": ANSWERS}
    truth = {"seed": seed, "problems": {}}
    plan = rng_for(seed, "plan")
    order = [KINDS[i % len(KINDS)] for i in range(N_PROBLEMS)]
    plan.shuffle(order)
    for i, kind in enumerate(order):
        qid = f"Q-{i + 1:02d}"
        rng = rng_for(seed, "q", qid)
        (ta, aa), (tb, ab) = kind(rng), kind(rng)
        while fmt(aa) == fmt(ab):  # two parts, two different answers
            tb, ab = kind(rng)
        files[f"problems/{qid}.md"] = f"# {qid}\n\n**(a)** {ta}\n\n**(b)** {tb}\n"
        truth["problems"][qid] = {"kind": kind.__name__, "a": fmt(aa), "b": fmt(ab),
                                  "unit_chars": len(ta) + len(tb) + 3000}
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def _norm(x):
    try:
        return fmt(Fraction(str(x).strip()))
    except (ValueError, ZeroDivisionError):
        return None


def grade(seed, answer):
    """Per problem, all or nothing: both parts exactly (any equal fraction form)."""
    truth = generate(seed)
    per = {}
    for qid, t in truth["problems"].items():
        got = answer.get(qid) if isinstance(answer.get(qid), dict) else {}
        per[qid] = float(all(got.get(part) is not None and _norm(got[part]) == t[part] for part in ("a", "b")))
    return {"reward": round(sum(per.values()) / len(per), 4), "problems": per}


def oracle(seed):
    return {q: {"a": t["a"], "b": t["b"]} for q, t in generate(seed)["problems"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["problems"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(ANSWERS) + 300}


ANSWER_PATH = "/workspace/answer/answers.json"
INSTRUCTION = """\
# Problem set answer key

The combinatorics problem set in `/workspace/problems/` needs an answer key.
Solve both parts of every problem exactly, in the format of `docs/ANSWERS.md`.

Write `/workspace/answer/answers.json`:

```json
{"Q-NN": {"a": "5/18", "b": "120"}}
```
"""

META = {
    "unit": "problem", "kind": "exact counting", "domain": "combinatorics and probability",
    "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "exact answers where one misread word (round, at least, with replacement) changes the count",
    "deliverable": "`/workspace/answer/answers.json`",
    "grading": "Per problem, all or nothing: both parts exactly. Reward is the mean.",
    "per_unit": "model the problem precisely -- what is distinguishable, what is ordered, which bound is "
                "inclusive -- count it, and check the count a second way",
    "traps": [
        "**Round tables**: rotations are the same seating.",
        "**Repeated letters** are indistinguishable.",
        "**At least / at most / exactly** and inclusive bounds.",
        "**With vs without replacement.**",
        "**Constraints on single variables** (upper bounds) in stars-and-bars problems.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
