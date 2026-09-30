#!/usr/bin/env python3
"""LH37 -- grade 48 student proofs: find the first invalid step, if any.

proofs/P-NN.md is one student's proof of a claim, in numbered steps. The
marking rubric (docs/MARKING.md) asks for the number of the first step that
does not follow -- from the claim's hypotheses, earlier steps and standard
facts -- or 0 if every step is valid.

Six kinds of proof (induction on a sum, divisibility by induction, AM-GM, the
irrationality of a square root, a geometric series, cancelling a common
factor), each with its own numbers, and flaws of two sorts:

- a slip in one step (a wrong next term, a dropped factor, a sign);
- a step whose words are standard but whose numbers make it false: "n divides
  p^2, so n divides p" is valid for n = 7 and invalid for n = 12; dividing by
  1 - r is fine for r != 1 and not "for every real r"; a factor that is only
  "a nonzero constant" when b + c != 0.

A true claim does not make a proof valid (sqrt(12) IS irrational), so every
step has to be checked with its own numbers.

    python3 lh37_proof_grading.py --seed 1 --out /fixture
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_PROOFS = 48
# "n divides p^2, so n divides p" holds exactly when n is square-free: primes and
# square-free composites (valid proofs), not n with a repeated prime factor.
SQUARE_FREE = [2, 3, 5, 7, 11, 13, 17, 19, 6, 10, 15, 21, 30, 35]
NOT_SQUARE_FREE = [8, 12, 18, 20, 24, 27, 28, 45, 50, 16, 36]


def sgn(v):
    return f"+ {v}" if v >= 0 else f"- {-v}"


# ------------------------------------------------------------------ the six proofs
# Each returns (claim, steps, first_bad_step) for one variant.

def arithmetic_sum(rng, variant):
    a, d = rng.randint(1, 9), rng.randint(2, 7)
    claim = (f"For every integer n >= 1, {a} + {a + d} + ... + ({a} + (n - 1)*{d}) "
             f"= n*(2*{a} + (n - 1)*{d})/2.")
    nxt = f"{a} + (k + 1)*{d}" if variant == 3 else f"{a} + k*{d}"
    add_d = 2 * d if variant == 3 else d
    lin = 2 * a + (d + 2 if variant == 5 else d)
    rhs_lin = 2 * a + (d - 1 if variant == 6 else d)
    base_d = "1" if variant == 1 else "0"
    base = (f"Base case n = 2: the left side is {a} + {a + d} = {2 * a + d}; the right side is "
            f"2*(2*{a} + 1*{d})/2 = {2 * a + d}." if variant == 7 else
            f"Base case n = 1: the left side is {a}; the right side is 1*(2*{a} + {base_d}*{d})/2 = {a}.")
    steps = [
        base,
        "Inductive hypothesis: assume the formula holds for n = k.",
        f"The (k + 1)-th term is {nxt}.",
        f"So the sum of the first k + 1 terms is k*(2*{a} + (k - 1)*{d})/2 + {nxt}.",
        f"Over a common denominator this is ({2 * a}k + {d}k^2 - {d}k + {2 * a} + {2 * add_d}k)/2 "
        f"= ({d}k^2 + {lin}k + {2 * a})/2." if variant != 3 else
        f"Over a common denominator this is ({2 * a}k + {d}k^2 - {d}k + {2 * a} + {2 * d}k + {2 * d})/2 "
        f"= ({d}k^2 + {2 * a + d}k + {2 * a + 2 * d})/2.",
        f"The formula for n = k + 1 gives (k + 1)*(2*{a} + k*{d})/2 = ({d}k^2 + {rhs_lin}k + {2 * a})/2.",
        "The two agree, so the formula holds for k + 1, and by induction for every n >= 1.",
    ]
    if variant == 3:  # the sum no longer matches; the student claims it does anyway
        steps[5] = f"The formula for n = k + 1 gives (k + 1)*(2*{a} + k*{d})/2 = ({d}k^2 + {2 * a + d}k + {2 * a})/2."
    bad = {0: 0, 1: 1, 3: 3, 5: 5, 6: 6, 7: 7}[variant]  # 7: base case n = 2, conclusion for n >= 1
    return claim, steps, bad


def divisibility(rng, variant):
    b = rng.randint(4, 13)
    divisors = [m for m in range(2, b) if (b - 1) % m == 0]
    m = rng.choice(divisors)
    if variant == 1:  # a modulus that does not divide b - 1: the base case is false
        m = rng.choice([x for x in range(2, b + 3) if (b - 1) % x != 0])
    claim = f"For every integer n >= 1, {m} divides {b}^n - 1."
    tail = f"{b}" if variant == 3 else f"({b} - 1)"
    steps = [
        f"Base case n = 1: {b}^1 - 1 = {b - 1}, which is divisible by {m}.",
        f"Assume {m} divides {b}^k - 1, say {b}^k - 1 = {m}t for an integer t.",
        f"Then {b}^(k+1) - 1 = {b}*({b}^k - 1) + {tail}.",
        f"= {b}*{m}t + {b - 1 if variant != 3 else b}.",
        f"Both terms are divisible by {m}, so {m} divides {b}^(k+1) - 1.",
        "By induction the claim holds for every n >= 1.",
    ]
    bad = {0: 0, 1: 1, 3: 3}[variant]
    return claim, steps, bad


def am_gm(rng, variant):
    s = rng.randint(2, 9)
    c = s * s
    domain = "every real x > 0" if variant != 1 else "every nonzero real x"
    claim = f"For {domain}, x + {c}/x >= {2 * s}."
    root = f"{c}" if variant == 3 else f"{s}"
    eq = f"{c}" if variant == 5 else f"{s}"
    steps = [
        f"For x > 0 we may write x = (sqrt x)^2 and {c}/x = (sqrt({c}/x))^2." if variant != 1 else
        f"For x != 0 we may write x = (sqrt x)^2 and {c}/x = (sqrt({c}/x))^2.",
        f"(sqrt x - sqrt({c}/x))^2 >= 0, since a square is never negative.",
        f"Expanding, x - 2*sqrt(x)*sqrt({c}/x) + {c}/x >= 0, and sqrt(x)*sqrt({c}/x) = sqrt({c}) = {root}.",
        f"So x + {c}/x >= {2 * s if variant != 3 else 2 * c}." if variant != 3 else
        f"So x + {c}/x >= {2 * c}, and in particular x + {c}/x >= {2 * s}.",
        f"Equality holds exactly when sqrt x = sqrt({c}/x), that is when x = {eq}.",
    ]
    bad = {0: 0, 1: 1, 3: 3, 5: 5}[variant]
    return claim, steps, bad


def irrational_root(rng, variant):
    n = rng.choice(SQUARE_FREE) if variant in (0, 2) else rng.choice(NOT_SQUARE_FREE)
    q2 = f"{n}q" if variant == 2 else f"{n}q^2"
    claim = f"sqrt({n}) is irrational."
    steps = [
        f"Suppose sqrt({n}) = p/q for positive integers p and q with no common factor.",
        f"Squaring, p^2 = {q2}.",
        f"So {n} divides p^2.",
        f"Therefore {n} divides p.",
        f"Write p = {n}r. Then {n * n}r^2 = {n}q^2, so q^2 = {n}r^2.",
        f"So {n} divides q^2, and therefore {n} divides q.",
        f"Then {n} divides both p and q, contradicting that they have no common factor.",
    ]
    bad = {0: 0, 2: 2, 4: 4}[variant]  # variant 4: n has a repeated prime factor, so step 4 fails
    return claim, steps, bad


def geometric(rng, variant):
    a = rng.randint(2, 9)
    domain = "every real r != 1" if variant != 5 else "every real r"
    claim = f"For {domain} and every n >= 1, {a} + {a}r + ... + {a}r^(n-1) = {a}(1 - r^n)/(1 - r)."
    sub = f"{a} - {a}r^(n+1)" if variant == 3 else f"{a} - {a}r^n"
    steps = [
        f"Let S = {a} + {a}r + ... + {a}r^(n-1).",
        f"Then rS = {a}r + {a}r^2 + ... + {a}r^n.",
        f"Subtracting, S - rS = {sub}.",
        f"So S(1 - r) = {a}(1 - r^n)." if variant != 3 else f"So S(1 - r) = {a}(1 - r^n) after cancelling.",
        "Since r != 1, dividing both sides by 1 - r gives the formula." if variant != 5 else
        "Dividing both sides by 1 - r gives the formula.",
    ]
    bad = {0: 0, 3: 3, 5: 5}[variant]
    return claim, steps, bad


def common_factor(rng, variant):
    a, b = rng.randint(1, 9), rng.randint(1, 9)
    c = -b if variant == 4 else rng.choice([x for x in range(-9, 10) if x not in (0, -b, b)])
    # the bracket (x - b) - (x + c) is -b - c; the slip writes -b + c
    bracket = f"-{b} + ({c})" if variant == 3 else f"-{b} - ({c})"
    claim = f"The only real solution of (x - {a})(x - {b}) = (x - {a})(x {sgn(c)}) is x = {a}."
    steps = [
        f"Bring everything to one side: (x - {a})(x - {b}) - (x - {a})(x {sgn(c)}) = 0.",
        f"Factor out (x - {a}): (x - {a})[(x - {b}) - (x {sgn(c)})] = 0.",
        f"The bracket simplifies to {bracket}, a nonzero constant.",
        f"So (x - {a}) times a nonzero constant is 0, which forces x = {a}.",
        f"Hence x = {a} is the only solution.",
    ]
    bad = {0: 0, 3: 3, 4: 3}[variant]
    return claim, steps, bad


KINDS = {
    # Logic flaws (a valid-looking move that these numbers or this domain break)
    # are weighted up, so checking arithmetic alone is not enough.
    "arithmetic_sum": (arithmetic_sum, [0, 1, 3, 5, 6, 7, 7]),
    "divisibility": (divisibility, [0, 1, 3]),
    "am_gm": (am_gm, [0, 1, 1, 3, 5]),
    "irrational_root": (irrational_root, [0, 0, 2, 4, 4]),
    "geometric": (geometric, [0, 3, 5, 5]),
    "common_factor": (common_factor, [0, 3, 4, 4]),
}

MARKING = """# Marking rubric

For each proof, give the number of the FIRST step that is not valid, or 0 if
every step is valid.

A step is valid if it follows from the claim's hypotheses, the earlier steps
and standard mathematical facts, for the numbers actually in it. A step that
merely repeats an earlier error is not the first invalid step; the earlier one
is. A step whose reasoning is standard but false for these particular numbers
(dividing by something that may be zero, a divisibility rule that only holds
for primes, a square root of a negative number) is invalid. Whether the claim
itself happens to be true does not matter: grade the proof.
"""


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    kinds = [k for k in KINDS for _ in range(N_PROOFS // len(KINDS))]
    rng.shuffle(kinds)
    files = {"docs/MARKING.md": MARKING}
    truth = {"seed": seed, "proofs": {}}
    students = ["A. Jansen", "B. Moreau", "C. Rossi", "D. Novak", "E. Silva", "F. Berg", "G. Costa", "H. Meyer"]
    for i, kind in enumerate(kinds):
        pid = f"P-{i + 1:02d}"
        prng = rng_for(seed, "proof", pid)
        fn, variants = KINDS[kind]
        variant = prng.choice(variants)
        claim, steps, bad = fn(prng, variant)
        text = [f"# {pid}", "", f"Student: {prng.choice(students)}", "", f"**Claim.** {claim}", "", "**Proof.**", ""]
        text += [f"{j + 1}. {s}" for j, s in enumerate(steps)]
        files[f"proofs/{pid}.md"] = "\n".join(text) + "\n"
        truth["proofs"][pid] = {"kind": kind, "first_bad_step": bad, "unit_chars": len(files[f"proofs/{pid}.md"]) + 2500}
    if out is not None:
        for rel, t in files.items():
            write(Path(out) / "workspace", rel, t)
    return truth


def grade(seed, answer):
    """Per proof: the first invalid step (0 if valid), exactly."""
    truth = generate(seed)
    per = {}
    for pid, t in truth["proofs"].items():
        got = answer.get(pid)
        got = got.get("first_invalid_step") if isinstance(got, dict) else got
        per[pid] = float(isinstance(got, int) and not isinstance(got, bool) and got == t["first_bad_step"])
    return {"reward": round(sum(per.values()) / len(per), 4), "proofs": per}


def oracle(seed):
    return {pid: {"first_invalid_step": t["first_bad_step"]} for pid, t in generate(seed)["proofs"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["proofs"].values()],
            "judgement_turns": 4, "orchestration_turns": 10, "shared_chars": len(MARKING) + 300}


ANSWER_PATH = "/workspace/answer/marks.json"
INSTRUCTION = """\
# Mark the proof assignment

Each file in `/workspace/proofs/` is one student's submitted proof. Mark every
one by `docs/MARKING.md`: the first step that is not valid, or 0 if the proof
is correct.

Write `/workspace/answer/marks.json`:

```json
{"P-NN": {"first_invalid_step": 0}}
```
"""

META = {
    "unit": "proof", "kind": "proof checking", "domain": "undergraduate mathematics",
    "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "step-by-step verification where the same sentence is valid or invalid depending on its numbers",
    "deliverable": "`/workspace/answer/marks.json`",
    "grading": "Per proof: the first invalid step (0 if valid), exactly. Reward is the mean.",
    "per_unit": "check every step against the claim, the earlier steps and the numbers in it: recompute each "
                "algebraic line, and ask whether each standard move (divide, take a root, use divisibility) is "
                "allowed here",
    "traps": [
        "**A true claim, an invalid proof**: sqrt(12) is irrational, but \"12 divides p^2, so 12 divides p\" is false.",
        "**Domains**: dividing by 1 - r for every real r; square roots for every nonzero x.",
        "**Degenerate numbers**: the bracket is \"a nonzero constant\" unless b + c = 0.",
        "**Slips** in one line (a wrong next term, a dropped factor) that later lines repeat: the FIRST is the answer.",
        "**Base cases** that are false for the given modulus.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
