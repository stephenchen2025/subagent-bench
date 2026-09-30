#!/usr/bin/env python3
"""Reference solution for LH37, from the workspace alone.

Reads proofs/*.md and follows docs/MARKING.md; never sees the generator. Each
worker marks one proof by checking it the way a careful marker would: redo
every piece of arithmetic with the proof's own numbers, and ask whether each
standard move is allowed here -- a divisibility rule that needs a square-free
modulus, a division that needs r != 1, a square root that needs x > 0, a
constant that is only nonzero when it is. The first step that fails is the
mark; 0 if none does.

    python3 solve.py /workspace
"""

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def ints(s):
    return [int(x) for x in re.findall(r"-?\d+", s)]


def square_free(n):
    return all(n % (p * p) for p in range(2, int(n ** 0.5) + 1))


def read(path):
    text = path.read_text()
    claim = re.search(r"\*\*Claim\.\*\* (.+)", text).group(1)
    steps = [m.group(1) for m in re.finditer(r"^\d+\. (.+)$", text, re.M)]
    return claim, steps


def check_arithmetic_sum(claim, steps):
    a, d = map(int, re.search(r"\((\d+) \+ \(n - 1\)\*(\d+)\) =", claim).groups())
    base_n = int(re.search(r"Base case n = (\d+)", steps[0]).group(1))
    if base_n == 1:
        coeff = int(re.search(r"1\*\(2\*\d+ \+ (\d+)\*\d+\)/2", steps[0]).group(1))
        if (2 * a + coeff * d) / 2 != a:
            return 1
    else:
        left = re.search(r"left side is .* = (\d+);", steps[0]).group(1)
        right = re.search(r"right side is .* = (\d+)\.", steps[0]).group(1)
        want = sum(a + i * d for i in range(base_n))
        if int(left) != want or int(right) != want:
            return 1
    # step 3: the (k+1)-th term is a + k*d
    term = re.search(r"term is (\d+) \+ (.+)\*(\d+)\.", steps[2])
    if not (int(term.group(1)) == a and term.group(2).strip() == "k" and int(term.group(3)) == d):
        return 3
    # step 5: k(2a + (k-1)d)/2 + a + kd = (d k^2 + (2a + d) k + 2a)/2
    lhs = re.search(r"\((\d+)k \+ (\d+)k\^2 - (\d+)k \+ (\d+) \+ (\d+)k\)/2", steps[4])
    rhs = [int(x) for x in re.search(r"= \((\d+)k\^2 \+ (\d+)k \+ (\d+)\)/2\.", steps[4]).groups()]
    if not lhs or [int(x) for x in lhs.groups()] != [2 * a, d, d, 2 * a, 2 * d] or rhs != [d, 2 * a + d, 2 * a]:
        return 5
    # step 6: (k+1)(2a + kd)/2 = (d k^2 + (2a + d) k + 2a)/2
    six = [int(x) for x in re.search(r"= \((\d+)k\^2 \+ (\d+)k \+ (\d+)\)/2\.", steps[5]).groups()]
    if six != [d, 2 * a + d, 2 * a]:
        return 6
    # step 7: the conclusion may only start where the base case did
    start = int(re.search(r"every n >= (\d+)", steps[6]).group(1))
    if start < base_n:
        return 7
    return 0


def check_divisibility(claim, steps):
    m, b = map(int, re.search(r"n >= 1, (\d+) divides (\d+)\^n - 1", claim).groups())
    value = int(re.search(r"\^1 - 1 = (\d+)", steps[0]).group(1))
    if value != b - 1 or value % m:
        return 1
    tail = steps[2].rsplit("+ ", 1)[1].rstrip(".")
    tail_value = eval(tail.replace(" ", ""), {"__builtins__": {}})  # "(13 - 1)" or "13": a number
    if tail_value != b - 1:
        return 3
    if int(steps[3].rsplit("+ ", 1)[1].rstrip(".")) != b - 1:
        return 4
    if (b - 1) % m:
        return 5
    return 0


def check_am_gm(claim, steps):
    c = int(re.search(r"x \+ (\d+)/x", claim).group(1))
    if "nonzero" in claim or "x != 0" in steps[0]:
        return 1  # sqrt(x) needs x >= 0; the proof does not cover negative x
    root = int(re.search(r"= sqrt\(\d+\) = (\d+)\.", steps[2]).group(1))
    if root * root != c:
        return 3
    bound = int(re.search(r">= (\d+)", steps[3]).group(1))
    if bound != 2 * root:
        return 4
    eq = int(re.search(r"x = (\d+)\.", steps[4]).group(1))
    if eq * eq != c:
        return 5
    return 0


def check_irrational(claim, steps):
    n = int(re.search(r"sqrt\((\d+)\)", claim).group(1))
    if not re.search(rf"p\^2 = {n}q\^2\.", steps[1]):
        return 2
    if not square_free(n):
        return 4  # n | p^2 does not give n | p when n has a repeated prime factor
    nn = int(re.search(r"Then (\d+)r\^2", steps[4]).group(1))
    if nn != n * n:
        return 5
    return 0


def check_geometric(claim, steps):
    if not re.search(r"S - rS = \d+ - \d+r\^n\.", steps[2]):
        return 3
    if "r != 1" not in claim:
        return 5  # dividing by 1 - r needs r != 1, which the claim does not assume
    return 0


def check_common_factor(claim, steps):
    b, c_sign, c_abs = re.search(r"\(x - \d+\)\(x - (\d+)\) = \(x - \d+\)\(x ([+-]) (\d+)\)", claim).groups()
    b, c = int(b), int(c_abs) * (1 if c_sign == "+" else -1)
    shown = re.search(r"simplifies to (.+), a nonzero constant", steps[2]).group(1)
    value = eval(shown.replace(" ", ""), {"__builtins__": {}})
    if value != -b - c or value == 0:
        return 3
    return 0



def mark(path):
    claim, steps = read(path)
    if "r^(n-1)" in claim:
        return path.stem, check_geometric(claim, steps)
    if "divides" in claim:
        return path.stem, check_divisibility(claim, steps)
    if "+ ... +" in claim:
        return path.stem, check_arithmetic_sum(claim, steps)
    if "/x >=" in claim:
        return path.stem, check_am_gm(claim, steps)
    if "is irrational" in claim:
        return path.stem, check_irrational(claim, steps)
    return path.stem, check_common_factor(claim, steps)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ws = Path(argv[0] if argv else "/workspace")
    with ThreadPoolExecutor(8) as pool:
        marks = dict(pool.map(mark, sorted((ws / "proofs").glob("P-*.md"))))
    out = ws / "answer" / "marks.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({pid: {"first_invalid_step": s} for pid, s in marks.items()}, indent=2) + "\n")
    print(f"{len(marks)} proofs marked, {sum(1 for s in marks.values() if s == 0)} valid")


if __name__ == "__main__":
    main()
