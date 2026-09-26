#!/usr/bin/env python3
"""LH15 -- make 40 slow functions fast without changing a single result.

perf/ holds 40 functions that are correct and far too slow: quadratic
membership scans, nested-loop joins, windows recomputed from scratch, trial
division, exponential recursion, `list.count` inside a loop. docs/BUDGET.md
gives each a size it must handle within a second. Every result must be
identical to today's, and "identical" includes the parts a hasty rewrite
changes: which of several tied items wins, output order, how duplicates pair
up, and case handling.

The grader imports the agent's module and runs it on hidden inputs, small ones
checked against the original slow code and large ones checked against a
reference, under a time limit. Faster-but-different scores zero for that
function, and so does correct-but-slow.

    python3 lh15_perf_fixes.py --seed 1 --out /fixture
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_FUNCTIONS = 40
TIME_LIMIT_S = 3.0  # the brief says 1 s; the grader allows slack for slow machines

# template: (slow source, fast reference, input maker source, variants)
# Input makers take (rng, n) and return the argument tuple.
T = {
    "dedupe": (
        '''def {fn}(items):
    """Items in first-seen order, without repeats{case_doc}."""
    out, seen_keys = [], []
    for item in items:
        key = {key}
        if key not in seen_keys:
            seen_keys.append(key)
            out.append(item)
    return out
''',
        '''def {fn}(items):
    out, seen = [], set()
    for item in items:
        key = {key}
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out
''',
        "lambda rng, n: ([rng.choice(['Alpha', 'alpha', 'Beta', 'beta', 'Gamma']) + str(rng.randrange(n // 3 + 1)) for _ in range(n)],)",
        [{"key": "item", "case_doc": ""}, {"key": "item.lower()", "case_doc": ", ignoring case"}]),
    "pair_count": (
        '''def {fn}(values, target):
    """How many index pairs i < j have values[i] + values[j] == target{abs_doc}."""
    count = 0
    for i in range(len(values)):
        for j in range(i + 1, len(values)):
            if {cond}:
                count += 1
    return count
''',
        '''def {fn}(values, target):
    from collections import Counter
    seen, count = Counter(), 0
    for v in values:
        for want in {wants}:
            count += seen[want]
        seen[v] += 1
    return count
''',
        "lambda rng, n: ([rng.randint(-50, 50) for _ in range(n)], rng.randint(-20, 20))",
        [{"cond": "values[i] + values[j] == target", "abs_doc": "", "wants": "(target - v,)"},
         {"cond": "abs(values[i] + values[j]) == abs(target)", "abs_doc": " in absolute value",
          "wants": "sorted({abs(target) - v, -abs(target) - v})"}]),
    "join": (
        '''def {fn}(left, right):
    """Inner join on `id`: one (left_row, right_row) per match, ordered by left
    row, then by right row{dup_doc}."""
    out = []
    for l in left:
        for r in right:
            if l["id"] == r["id"]{extra}:
                out.append((l, r))
    return out
''',
        '''def {fn}(left, right):
    index = {{}}
    for r in right:
        index.setdefault(r["id"], []).append(r)
    out = []
    for l in left:
        for r in index.get(l["id"], []):
            if True{extra}:
                out.append((l, r))
    return out
''',
        "lambda rng, n: ([{'id': rng.randrange(n // 2 + 1), 'v': i} for i in range(n)], [{'id': rng.randrange(n // 2 + 1), 'w': i, 'active': rng.random() < 0.7} for i in range(n)])",
        [{"extra": "", "dup_doc": ""}, {"extra": ' and r["active"]', "dup_doc": "; inactive right rows never match"}]),
    "window_max": (
        '''def {fn}(values, k):
    """{what} of every window of `k` consecutive values, left to right."""
    return [{agg}(values[i:i + k]) for i in range(len(values) - k + 1)]
''',
        '''def {fn}(values, k):
    from collections import deque
    out, dq = [], deque()
    for i, v in enumerate(values):
        while dq and dq[0] <= i - k:
            dq.popleft()
        while dq and values[dq[-1]] {cmp} v:
            dq.pop()
        dq.append(i)
        if i >= k - 1:
            out.append(values[dq[0]])
    return out
''',
        "lambda rng, n: ([rng.randint(0, 1000) for _ in range(n)], max(1, n // 10))",
        [{"what": "The maximum", "agg": "max", "cmp": "<="}, {"what": "The minimum", "agg": "min", "cmp": ">="}]),
    "distinct_kgrams": (
        '''def {fn}(text, k):
    """How many distinct substrings of length `k` does `text` contain{case_doc}?"""
    seen = []
    for i in range(len(text) - k + 1):
        gram = text[i:i + k]{norm}
        if gram not in seen:
            seen.append(gram)
    return len(seen)
''',
        '''def {fn}(text, k):
    return len({{text[i:i + k]{norm} for i in range(len(text) - k + 1)}})
''',
        "lambda rng, n: (''.join(rng.choice('abcdeABCDE') for _ in range(n)), 6)",
        [{"norm": "", "case_doc": ""}, {"norm": ".lower()", "case_doc": ", ignoring case"}]),
    "primes": (
        '''def {fn}(limit):
    """{what} below `limit`."""
    found = []
    for n in range(2, limit):
        if all(n % d for d in range(2, n)):
            found.append(n)
    return {ret}
''',
        '''def {fn}(limit):
    if limit < 3:
        found = []
    else:
        sieve = bytearray([1]) * limit
        sieve[0:2] = b"\\x00\\x00"
        for p in range(2, int(limit ** 0.5) + 1):
            if sieve[p]:
                sieve[p * p::p] = bytearray(len(range(p * p, limit, p)))
        found = [i for i in range(limit) if sieve[i]]
    return {ret}
''',
        "lambda rng, n: (n * 4 + rng.randint(0, 9),)",
        [{"what": "Every prime", "ret": "found"}, {"what": "The sum of the primes", "ret": "sum(found)"}]),
    "tribonacci": (
        '''def {fn}(n):
    """The n-th term (0-based) of T(n) = T(n-1) + T(n-2) + T(n-3) with T(0..2) = {seed_doc}, modulo {mod}."""
    if n < 3:
        return {seeds}[n] % {mod}
    return ({fn}(n - 1) + {fn}(n - 2) + {fn}(n - 3)) % {mod}
''',
        '''def {fn}(n):
    a, b, c = {seeds}
    if n < 3:
        return (a, b, c)[n] % {mod}
    for _ in range(n - 2):
        a, b, c = b, c, (a + b + c) % {mod}
    return c
''',
        "lambda rng, n: (min(n, 18) + rng.randint(0, 2),)",
        [{"seeds": "(0, 0, 1)", "seed_doc": "0, 0, 1", "mod": "1000003"},
         {"seeds": "(1, 1, 2)", "seed_doc": "1, 1, 2", "mod": "998244353"}]),
    "most_common": (
        '''def {fn}(words):
    """The most frequent word{case_doc}; on a tie, the one that appears first."""
    words = [w{norm} for w in words]
    return max(words, key=words.count) if words else None
''',
        '''def {fn}(words):
    from collections import Counter
    words = [w{norm} for w in words]
    if not words:
        return None
    counts = Counter(words)
    best = max(counts.values())
    return next(w for w in words if counts[w] == best)
''',
        "lambda rng, n: ([rng.choice(['Red', 'red', 'Blue', 'blue', 'green', 'Green', 'teal']) for _ in range(n)],)",
        [{"norm": "", "case_doc": ""}, {"norm": ".lower()", "case_doc": ", ignoring case"}]),
}
# Sized so the original code needs 10x the limit or more, and the reference well under it.
SIZES = {"dedupe": 100000, "pair_count": 50000, "join": 25000, "window_max": 200000, "distinct_kgrams": 60000,
         "primes": 40000, "tribonacci": 200000, "most_common": 40000}


def _fmt(text, f):
    for k, v in f.items():
        text = text.replace("{" + k + "}", v)
    return text.replace("{{", "{").replace("}}", "}")


def plan(seed):
    rng = rng_for(seed, "plan")
    units = []
    for i in range(N_FUNCTIONS):
        tpl = list(T)[i % len(T)]
        fields = dict(T[tpl][3][(i // len(T)) % len(T[tpl][3])])
        fields["fn"] = f"{rng.choice(['compute', 'find', 'build', 'get'])}_{tpl}"
        units.append({"module": f"{tpl}_{i:02d}", "template": tpl, "fields": fields})
    return units


def generate(seed, out=None):
    truth = {"seed": seed, "modules": {}}
    files = {"perf/__init__.py": ""}
    budget = ["# Performance budget", "", "Each function must finish on the given input size within 1 second "
              "on one core, and return exactly what it returns today for every input.", "",
              "| module | function | size |", "|---|---|---|"]
    for u in plan(seed):
        slow, fast, maker, _ = T[u["template"]]
        src = _fmt(slow, u["fields"])
        files[f"perf/{u['module']}.py"] = f'"""{u["module"]}."""\n\n\n{src}'
        size = SIZES[u["template"]]
        what = {"tribonacci": f"n = {size}", "primes": f"limit = {size * 4}"}.get(u["template"], f"{size:,} items")
        budget.append(f"| `perf/{u['module']}.py` | `{u['fields']['fn']}` | {what} |")
        truth["modules"][u["module"]] = {"template": u["template"], "fn": u["fields"]["fn"], "slow": src,
                                        "fast": _fmt(fast, u["fields"]), "unit_chars": len(src) + 2500}
    files["docs/BUDGET.md"] = "\n".join(budget) + "\n"
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


CHECK = r'''import importlib.util, json, pickle, random, sys, time
spec = importlib.util.spec_from_file_location("m", sys.argv[1]); mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
cases = pickle.load(open(sys.argv[2], "rb"))
fn = getattr(mod, sys.argv[3])
results = []
for args in cases["small"]:
    results.append(repr(fn(*args)))
start = time.perf_counter()
big = repr(fn(*cases["large"]))
print(json.dumps({"small": results, "large": big, "seconds": time.perf_counter() - start}))
'''


def _cases(seed, info):
    import random
    rng = random.Random(f"{seed}|cases|{info['fn']}|{info['template']}")
    maker = eval(T[info["template"]][2])  # noqa: S307 -- generator-owned source
    small = [maker(rng, n) for n in (0, 1, 2, 3, 7, 25, 60)] if info["template"] != "tribonacci" else \
        [maker(rng, n) for n in (0, 1, 2, 5, 12, 20, 24)]
    size = SIZES[info["template"]]
    large = (size,) if info["template"] == "tribonacci" else maker(rng, size)
    return {"small": small, "large": large}


def _run(path, cases, fn, tmp, timeout):
    import pickle
    case_file = Path(tmp) / "cases.pkl"
    case_file.write_bytes(pickle.dumps(cases))
    check = Path(tmp) / "check.py"
    check.write_text(CHECK)
    try:
        run = subprocess.run([sys.executable, str(check), str(path), str(case_file), fn],
                             capture_output=True, text=True, timeout=timeout)
        return json.loads(run.stdout) if run.returncode == 0 else None
    except (subprocess.TimeoutExpired, ValueError):
        return None


def grade(seed, workspace):
    """Per function: identical results to the original on small hidden inputs,
    identical to the reference on a large one, and the large one inside the time
    limit. All or nothing per function; reward is the mean."""
    truth, _ = generate(seed)
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        for mod, info in truth["modules"].items():
            path = Path(workspace) / "perf" / f"{mod}.py"
            if not path.exists():
                per[mod] = 0.0
                continue
            cases = _cases(seed, info)
            ref_slow = Path(tmp) / "slow.py"
            ref_slow.write_text(info["slow"])
            ref_fast = Path(tmp) / "fast.py"
            ref_fast.write_text(info["fast"])
            want_small = _run(ref_slow, {"small": cases["small"], "large": cases["small"][0]}, info["fn"], tmp, 120)
            want_large = _run(ref_fast, {"small": [], "large": cases["large"]}, info["fn"], tmp, 120)
            got = _run(path, cases, info["fn"], tmp, TIME_LIMIT_S + 5)
            ok = (got is not None and want_small is not None and want_large is not None
                  and got["small"] == want_small["small"] and got["large"] == want_large["large"]
                  and got["seconds"] <= TIME_LIMIT_S)
            per[mod] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "modules": per}


def solve(seed, workspace):
    truth, _ = generate(seed)
    for mod, info in truth["modules"].items():
        write(Path(workspace) / "perf", f"{mod}.py", f'"""{mod}."""\n\n\n{info["fast"]}')


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [m["unit_chars"] for m in t["modules"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": 2000}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Hit the performance budget

Every function in `/workspace/perf/` is correct and far too slow for
production traffic. `docs/BUDGET.md` gives the input size each must handle in
under a second.

Make each one fast enough. Every function must keep returning exactly what it
returns today, for every input: same values, same order, same winner on ties.
Keep module and function names and signatures unchanged.
"""

META = {
    "unit": "function", "kind": "optimisation", "domain": "algorithmic complexity", "output_tokens": 1800, "needs_pytest": False,
    "failure_mode": "optimisation under an exact-equivalence contract",
    "deliverable": "rewritten modules under `perf/`",
    "grading": "Per function: identical results to the original on small hidden inputs and to a reference "
               "on a large one, within the time limit. All or nothing per function; reward is the mean.",
    "per_unit": "find the complexity bottleneck, pick a faster algorithm, and make sure it preserves every "
                "observable detail: order, tie-breaking, duplicate pairing, case handling, edge sizes",
    "traps": [
        "**Tie-breaking.** `max(words, key=words.count)` returns the first of several tied words; "
        "`Counter.most_common` must be used carefully to match.",
        "**Duplicate semantics.** Pair counting over repeated values, and joins that must keep right-row order.",
        "**Variants.** Case-insensitive, absolute-value, minimum-instead-of-maximum and sum-instead-of-list "
        "versions sit next to their plain siblings.",
        "**Edge sizes.** Empty inputs, windows as large as the input, limits below 3.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
