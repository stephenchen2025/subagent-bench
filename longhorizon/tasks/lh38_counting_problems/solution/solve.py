#!/usr/bin/env python3
"""Reference solution for LH38, from the workspace alone.

Reads problems/*.md and docs/ANSWERS.md; never sees the generator. Each worker
takes one problem: it reads each part literally -- a row or a round table,
exactly or at least, with or without replacement, which bounds apply -- and
counts by direct enumeration, so no formula can be misapplied. Answers are
exact integers or fractions in lowest terms.

    python3 solve.py /workspace
"""

import itertools
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path


def fmt(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def letters(q):
    word = re.search(r"letters of (?:the word )?([A-Z]+)", q).group(1)
    perms = set(itertools.permutations(word))
    if "no two identical letters next to each other" in q:
        perms = {p for p in perms if all(p[i] != p[i + 1] for i in range(len(p) - 1))}
    elif "vowels in one consecutive block" in q:
        def block(p):
            idx = [i for i, ch in enumerate(p) if ch in "AEIOU"]
            return max(idx) - min(idx) == len(idx) - 1
        perms = {p for p in perms if block(p)}
    elif "begin and end with the same letter" in q:
        perms = {p for p in perms if p[0] == p[-1]}
    return len(perms)


def dice(q):
    k, n = map(int, re.search(r"(\d+) fair (\d+)-sided dice", q).groups())
    cmp, s = re.search(r"total is (exactly|at least|at most) (\d+)", q).groups()
    s = int(s)
    rolls = list(itertools.product(range(1, n + 1), repeat=k))
    test = {"exactly": lambda t: t == s, "at least": lambda t: t >= s, "at most": lambda t: t <= s}[cmp]
    return Fraction(sum(1 for r in rolls if test(sum(r))), len(rolls))


def committee(q):
    men, women = map(int, re.search(r"(\d+) men and (\d+) women", q).groups())
    size = int(re.search(r"committees of (\d+)", q).group(1))
    need = int(re.search(r"at least (\d+) wom", q).group(1))
    feud = "refuse to serve together" in q
    people = [("M", i) for i in range(men)] + [("W", i) for i in range(women)]
    count = 0
    for c in itertools.combinations(people, size):
        if sum(p[0] == "W" for p in c) >= need and not (feud and ("M", 0) in c and ("W", 0) in c):
            count += 1
    return count


def bounded_sum(q):
    k, n = map(int, re.search(r"x1 \+ \.\.\. \+ x(\d+) = (\d+)", q).groups())
    lo, hi = [0] * k, [n] * k
    for i, a, b in re.findall(r"(\d+) <= x(\d+) <= (\d+)", q):
        lo[int(a) - 1], hi[int(a) - 1] = int(i), int(b)
    for a, b in re.findall(r"x(\d+) >= (\d+)", q):
        lo[int(a) - 1] = int(b)
    return sum(1 for xs in itertools.product(*[range(lo[j], hi[j] + 1) for j in range(k)]) if sum(xs) == n)


def lattice(q):
    pts = [tuple(map(int, t)) for t in re.findall(r"\((\d+), (\d+)\)", q)]
    (a, b), point = pts[1], pts[2]
    avoid = "never pass through" in q
    count = 0
    for ups in itertools.combinations(range(a + b), b):
        x = y = 0
        hit = False
        for i in range(a + b):
            x, y = (x, y + 1) if i in ups else (x + 1, y)
            hit |= (x, y) == point
        count += (not hit) if avoid else hit
    return count


def cards(q):
    ranks, suits = map(int, re.search(r"(\d+) ranks in each of (\d+) suits", q).groups())
    hand = int(re.search(r"cards\)\. (\d+) cards are dealt", q).group(1))
    deck = list(itertools.product(range(ranks), range(suits)))
    ok = total = 0
    for h in itertools.combinations(deck, hand):
        total += 1
        per_rank = sorted((sum(c[0] == r for c in h) for r in range(ranks)), reverse=True)
        if "exactly one pair" in q:
            ok += per_rank[0] == 2 and per_rank[1] < 2
        elif "no two cards of the same rank" in q:
            ok += per_rank[0] == 1
        else:
            ok += len({c[1] for c in h}) == suits
    return Fraction(ok, total)


def seating(q):
    n = int(re.search(r"^(\d+) people", q).group(1))
    a, b = re.search(r"including (\w+) and (\w+)", q).groups()
    together = "not next to each other" not in q
    round_table = "round table" in q
    people = [a, b] + [f"p{i}" for i in range(n - 2)]
    count = 0
    for p in itertools.permutations(people):
        if round_table and p[0] != a:  # fix a's seat: one representative per rotation
            continue
        i, j = p.index(a), p.index(b)
        adjacent = abs(i - j) == 1 or (round_table and abs(i - j) == n - 1)
        count += adjacent == together
    return count


def urn(q):
    red, blue = map(int, re.search(r"(\d+) red and (\d+) blue", q).groups())
    draws = int(re.search(r"(\d+) balls are drawn", q).group(1))
    need = int(re.search(r"at least (\d+) of them are red", q).group(1))
    balls = ["R"] * red + ["B"] * blue
    seqs = (itertools.product(range(len(balls)), repeat=draws) if "with replacement" in q
            else itertools.permutations(range(len(balls)), draws))
    total = ok = 0
    for s in seqs:
        total += 1
        ok += sum(balls[i] == "R" for i in s) >= need
    return Fraction(ok, total)


def solve_part(q):
    if "arrangements" in q:
        return letters(q)
    if "dice" in q:
        return dice(q)
    if "committees" in q:
        return committee(q)
    if "integer solutions" in q:
        return bounded_sum(q)
    if "path on the grid" in q:
        return lattice(q)
    if "deck has" in q:
        return cards(q)
    if "people, including" in q:
        return seating(q)
    return urn(q)


def solve_problem(path):
    text = path.read_text()
    parts = dict(re.findall(r"\*\*\((a|b)\)\*\* (.+)", text))
    return path.stem, {k: fmt(solve_part(v.strip())) for k, v in parts.items()}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        answers = dict(pool.map(solve_problem, sorted((ws / "problems").glob("Q-*.md"))))
    out = ws / "answer" / "answers.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(answers, indent=2) + "\n")
    print(f"{len(answers)} problems solved")


if __name__ == "__main__":
    main()
