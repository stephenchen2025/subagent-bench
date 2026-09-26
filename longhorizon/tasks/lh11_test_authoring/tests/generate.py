#!/usr/bin/env python3
"""LH11 -- write the missing tests for 40 utility modules, graded by mutants.

lib/ holds 40 small modules, each with one public function whose docstring is
its specification: edge cases, error cases, rounding rules. None has tests. The
brief asks for tests/test_<module>.py for every module.

Grading is mutation testing. For each module the grader keeps a set of planted
mutants -- each a one-line change that breaks exactly one sentence of the
docstring (an off-by-one bound, a rounding mode, a missing error). A module
scores the fraction of its mutants the agent's tests kill, and zero if those
tests fail against the real code. A smoke test that calls the function once
kills almost nothing. Only tests that pin each edge the docstring states do.

Tests that read the source instead of exercising it (inspect, open, hashing
__file__) are refused: that would kill mutants without testing anything.

    python3 lh11_test_authoring.py --seed 1 --out /fixture
"""

import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, rng_for, run_pytest, standard_main, write  # noqa: E402

N_MODULES = 40

# Each template: (source, oracle tests, mutants). `{fn}` is the function name;
# other fields come from the variant. Oracle tests must pass on the source and
# fail on every mutant -- test_longhorizon verifies that, so no mutant is
# equivalent to the original.
TEMPLATES = {
    "clamp": (
        '''def {fn}(value, low, high):
    """Clamp `value` into the closed interval [low, high].

    Raises ValueError if low > high (low == high is allowed and returns low).
    A value already inside the interval is returned unchanged.
    """
    if low > high:
        raise ValueError("low must not exceed high")
    if value < low:
        return low
    if value > high:
        return high
    return value
''',
        '''def test_inside(): assert {fn}(5, 1, 10) == 5
def test_below(): assert {fn}(-3, 1, 10) == 1
def test_above(): assert {fn}(99, 1, 10) == 10
def test_equal_bounds(): assert {fn}(7, 4, 4) == 4
def test_inverted():
    with pytest.raises(ValueError): {fn}(1, 5, 2)
''',
        [("if low > high:", "if low >= high:"), ("return high", "return value"),
         ('raise ValueError("low must not exceed high")', "pass"), ("return low", "return value")]),
    "roman": (
        '''_PAIRS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
          (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def {fn}(number):
    """Return `number` in Roman numerals, {case}case.

    Valid input is 1 to 3999 inclusive; anything else raises ValueError.
    Subtractive forms are used (4 is IV, 900 is CM).
    """
    if not 1 <= number <= 3999:
        raise ValueError(number)
    out = []
    for value, glyph in _PAIRS:
        while number >= value:
            out.append(glyph)
            number -= value
    return "".join(out){casefn}
''',
        '''def test_small(): assert {fn}(4) == {wrap}("IV")
def test_mixed(): assert {fn}(1994) == {wrap}("MCMXCIV")
def test_max(): assert {fn}(3999) == {wrap}("MMMCMXCIX")
def test_nine_hundred(): assert {fn}(900) == {wrap}("CM")
def test_zero():
    with pytest.raises(ValueError): {fn}(0)
def test_too_big():
    with pytest.raises(ValueError): {fn}(4000)
''',
        [("1 <= number <= 3999", "1 <= number < 3999"), ('(900, "CM"), ', ""),
         ("while number >= value:", "while number > value:"), ("1 <= number", "0 <= number")]),
    "luhn": (
        '''def {fn}(text):
    """True if `text` is a valid Luhn number.

    Spaces {sepword} are ignored. Any other non-digit makes it invalid, and so
    does having fewer than 2 digits.
    """
    digits = text.replace(" ", ""){sepstrip}
    if not digits.isdigit() or len(digits) < 2:
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0
''',
        '''def test_valid(): assert {fn}("79927398713")
def test_invalid(): assert not {fn}("79927398710")
def test_spaces(): assert {fn}("7992 7398 713")
def test_sep(): assert {fn}("7992{sep}7398{sep}713")
def test_letters(): assert not {fn}("7992a398713")
def test_single_digit(): assert not {fn}("0")
def test_double_nine(): assert {fn}("59")
''',
        [("len(digits) < 2", "len(digits) < 1"), ("if i % 2 == 1:", "if i % 2 == 0:"),
         ("d -= 9", "d -= 10"), ('.replace(" ", "")', "")]),
    "semver": (
        '''def {fn}(a, b):
    """Compare two versions MAJOR.MINOR.PATCH[-PRERELEASE]: return -1, 0 or 1.

    Numeric parts compare as numbers (1.10.0 > 1.9.0). A prerelease sorts
    before its release (1.0.0-rc1 < 1.0.0); two prereleases compare as strings.
    """
    def parse(v):
        core, _, pre = v.partition("-")
        return tuple(int(x) for x in core.split(".")), pre

    (ca, pa), (cb, pb) = parse(a), parse(b)
    if ca != cb:
        return -1 if ca < cb else 1
    if pa == pb:
        return 0
    if not pa:
        return 1
    if not pb:
        return -1
    return -1 if pa < pb else 1
''',
        '''def test_equal(): assert {fn}("1.2.3", "1.2.3") == 0
def test_numeric(): assert {fn}("1.10.0", "1.9.0") == 1
def test_less(): assert {fn}("1.2.3", "1.3.0") == -1
def test_pre_before_release(): assert {fn}("1.0.0-rc1", "1.0.0") == -1
def test_release_after_pre(): assert {fn}("1.0.0", "1.0.0-rc1") == 1
def test_two_pres(): assert {fn}("1.0.0-alpha", "1.0.0-beta") == -1
''',
        [("tuple(int(x) for x in core.split(\".\"))", "tuple(core.split(\".\"))"),
         ("if not pa:\n        return 1", "if not pa:\n        return -1"),
         ("if not pb:\n        return -1", "if not pb:\n        return 1"),
         ("return -1 if pa < pb else 1", "return 1 if pa < pb else -1")]),
    "duration": (
        '''import re

_UNITS = {{"h": 3600, "m": 60, "s": 1}}


def {fn}(text):
    """Parse a duration like "1h30m", "90m" or "45s" into whole seconds.

    Units are h, m and s, each at most once, in that order; {caseword}.
    An empty string or anything else raises ValueError.
    """
    match = re.fullmatch(r"(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?", text{lower})
    if not text or not match:
        raise ValueError(text)
    h, m, s = (int(g) if g else 0 for g in match.groups())
    return h * _UNITS["h"] + m * _UNITS["m"] + s
''',
        '''def test_hm(): assert {fn}("1h30m") == 5400
def test_minutes(): assert {fn}("90m") == 5400
def test_all(): assert {fn}("2h0m5s") == 7205
def test_seconds(): assert {fn}("45s") == 45
def test_case(): assert {casecheck}
def test_empty():
    with pytest.raises(ValueError): {fn}("")
def test_order():
    with pytest.raises(ValueError): {fn}("5s1h")
''',
        [('"m": 60', '"m": 100'), ("if not text or not match:", "if not match:"),
         ('h * _UNITS["h"] + m * _UNITS["m"] + s', 'h * _UNITS["h"] + m * _UNITS["m"]'),
         ('"h": 3600', '"h": 360')]),
    "business_days": (
        '''import datetime


def {fn}(start, days, holidays=()):
    """Return the date `days` business days after `start`.

    Business days are Monday to Friday, excluding any date in `holidays`.
    days == 0 returns `start` unchanged, even on a weekend. Negative days
    raise ValueError.
    """
    if days < 0:
        raise ValueError(days)
    current = start
    while days > 0:
        current += datetime.timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            days -= 1
    return current
''',
        '''import datetime
D = datetime.date
def test_zero(): assert {fn}(D(2026, 9, 26), 0) == D(2026, 9, 26)
def test_over_weekend(): assert {fn}(D(2026, 9, 25), 1) == D(2026, 9, 28)
def test_week(): assert {fn}(D(2026, 9, 21), 5) == D(2026, 9, 28)
def test_holiday(): assert {fn}(D(2026, 9, 25), 1, {{D(2026, 9, 28)}}) == D(2026, 9, 29)
def test_negative():
    with pytest.raises(ValueError): {fn}(D(2026, 9, 21), -1)
''',
        [("current.weekday() < 5", "current.weekday() < 6"), (" and current not in holidays", ""),
         ("if days < 0:", "if days < -1:"), ("while days > 0:", "while days > 1:")]),
    "money": (
        '''from decimal import ROUND_HALF_EVEN, Decimal


def {fn}(amount):
    """Round `amount` to {places} decimal places, half to even (banker's rounding).

    Accepts int, float, str or Decimal; returns a Decimal. Floats are converted
    through str() first so that 2.675 rounds as the decimal 2.675.
    """
    quantum = Decimal(1).scaleb(-{places})
    return Decimal(str(amount)).quantize(quantum, rounding=ROUND_HALF_EVEN)
''',
        '''from decimal import Decimal
def test_half_even_down(): assert {fn}("{half_down}") == Decimal("{half_down_r}")
def test_half_even_up(): assert {fn}("{half_up}") == Decimal("{half_up_r}")
def test_float(): assert {fn}({flt}) == Decimal("{flt_r}")
def test_int(): assert {fn}(3) == Decimal("{int_r}")
''',
        [("ROUND_HALF_EVEN)", "ROUND_HALF_UP)"), ("Decimal(str(amount))", "Decimal(amount)"),
         ("scaleb(-{places})", "scaleb(-{places_minus})"), ("import ROUND_HALF_EVEN, Decimal", "import ROUND_HALF_UP as ROUND_HALF_EVEN, Decimal")]),
    "slug": (
        '''import re
import unicodedata


def {fn}(text):
    """Make a URL slug: ASCII-fold accents, lowercase, runs of anything that is
    not a letter or digit become a single "{sep}", and no leading or trailing
    "{sep}". An input with no letters or digits gives "".
    """
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "{sep}", folded.lower())
    return slug.strip("{sep}")
''',
        '''def test_basic(): assert {fn}("Hello World") == "hello{sep}world"
def test_accents(): assert {fn}("Crème Brûlée") == "creme{sep}brulee"
def test_runs(): assert {fn}("a -- b") == "a{sep}b"
def test_edges(): assert {fn}("  !Hi!  ") == "hi"
def test_empty(): assert {fn}("!!!") == ""
def test_digits(): assert {fn}("Route 66") == "route{sep}66"
''',
        [('r"[^a-z0-9]+"', 'r"[^a-z0-9]"'), ('.strip("{sep}")', ""), ("folded.lower()", "folded"),
         ('r"[^a-z0-9]+"', 'r"[^a-z]+"')]),
    "chunk": (
        '''def {fn}(items, size):
    """Split `items` into consecutive {kind}s of length `size`.

    The last {kind} may be shorter; nothing is dropped. size must be >= 1,
    otherwise ValueError.
    """
    if size < 1:
        raise ValueError(size)
    items = list(items)
    return [{ctor}(items[i:i + size]) for i in range(0, len(items), size)]
''',
        '''def test_even(): assert {fn}([1, 2, 3, 4], 2) == [{ctor}([1, 2]), {ctor}([3, 4])]
def test_partial(): assert {fn}([1, 2, 3], 2) == [{ctor}([1, 2]), {ctor}([3])]
def test_one(): assert {fn}([1, 2], 1) == [{ctor}([1]), {ctor}([2])]
def test_empty(): assert {fn}([], 3) == []
def test_zero():
    with pytest.raises(ValueError): {fn}([1], 0)
''',
        [("raise ValueError(size)", "return []"), ("range(0, len(items), size)", "range(0, len(items) - size + 1, size)"),
         ("items[i:i + size]", "items[i:i + size - 1]"), ("{ctor}(items[i:", "{other}(items[i:")]),
    "pct": (
        '''def {fn}(old, new):
    """Percentage change from `old` to `new`, rounded to {digits} decimal place(s).

    Returns None when old is 0 (the change is undefined). A fall is negative.
    """
    if old == 0:
        return None
    return round((new - old) / abs(old) * 100, {digits})
''',
        '''def test_rise(): assert {fn}(50, 75) == 50.0
def test_fall(): assert {fn}(200, 150) == -25.0
def test_zero(): assert {fn}(0, 10) is None
def test_negative_base(): assert {fn}(-50, -25) == 50.0
def test_rounding(): assert {fn}(3, 4) == {third}
''',
        [("if old == 0:", "if old == 0 and new == 0:"), ("abs(old)", "old"),
         ("(new - old)", "(old - new)"), (", {digits})", ", {digits_plus})")]),
}

VARIANT_FIELDS = {
    "clamp": [{}], "semver": [{}], "business_days": [{}],
    "roman": [{"case": "upper", "casefn": "", "wrap": ""},
              {"case": "lower", "casefn": ".lower()", "wrap": "str.lower"}],
    "luhn": [{"sepword": "and hyphens", "sepstrip": '.replace("-", "")', "sep": "-"},
             {"sepword": "and dots", "sepstrip": '.replace(".", "")', "sep": "."}],
    "duration": [{"caseword": "units are case-insensitive", "lower": ".lower()",
                  "casecheck": '{fn}("1H") == 3600'},
                 {"caseword": "units must be lowercase", "lower": "",
                  "casecheck": 'pytest.raises(ValueError, {fn}, "1H")'}],
    "money": [{"places": 2, "places_minus": 1, "half_down": "0.125", "half_down_r": "0.12",
               "half_up": "0.135", "half_up_r": "0.14", "flt": 2.675, "flt_r": "2.68", "int_r": "3.00"},
              {"places": 3, "places_minus": 2, "half_down": "0.0125", "half_down_r": "0.012",
               "half_up": "0.0135", "half_up_r": "0.014", "flt": 2.0045, "flt_r": "2.004", "int_r": "3.000"}],
    "slug": [{"sep": "-"}, {"sep": "_"}],
    "chunk": [{"kind": "list", "ctor": "list", "other": "tuple"},
              {"kind": "tuple", "ctor": "tuple", "other": "list"}],
    "pct": [{"digits": 1, "digits_plus": 2, "third": 33.3}, {"digits": 2, "digits_plus": 3, "third": 33.33}],
}
FORBIDDEN_IN_TESTS = ["inspect", "getsource", "__file__", "open(", "read_text", "hashlib", "__code__",
                      "co_code", "linecache", "importlib.util"]


def _fmt(text, fields):
    out = text
    for k, v in fields.items():
        out = out.replace("{" + k + "}", str(v))
    return out.replace("{{", "{").replace("}}", "}")


def plan(seed, n=N_MODULES):
    rng = rng_for(seed, "plan")
    units = []
    names = list(TEMPLATES)
    for i in range(n):
        tpl = names[i % len(names)]
        fields = dict(rng.choice(VARIANT_FIELDS[tpl]))
        mod = f"{tpl}_{rng.choice(['core', 'util', 'fmt', 'calc', 'text', 'kit'])}_{i:02d}"
        fields["fn"] = rng.choice(["compute", "apply", "to", "make", "get"]) + f"_{tpl}"
        units.append({"module": mod, "template": tpl, "fields": fields})
    return units


def unit_sources(u):
    src, tests, mutants = TEMPLATES[u["template"]]
    f = u["fields"]
    source = _fmt(src, f)
    oracle = "import pytest\n\nfrom lib." + u["module"] + " import " + f["fn"] + "\n\n\n" + _fmt(tests, f)
    muts = [(_fmt(a, f), _fmt(b, f)) for a, b in mutants]
    return source, oracle, muts


def generate(seed, out=None, n=N_MODULES):
    truth = {"seed": seed, "modules": {}}
    files = {"lib/__init__.py": "", "tests/__init__.py": "",
             "pytest.ini": "[pytest]\naddopts = -q -p no:cacheprovider --import-mode=importlib\n",
             "tests/conftest.py": "import sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n",
             "README.md": "# kit\n\nUtility modules. Each public function's docstring is its specification.\n"}
    for u in plan(seed, n):
        rng = rng_for(seed, "unit", u["module"])
        source, oracle, muts = unit_sources(u)
        helpers = "\n\n".join(filler_function(rng, f"_{u['template']}_helper_{k}") for k in range(rng.randint(2, 4)))
        files[f"lib/{u['module']}.py"] = f'"""{u["module"]}."""\n\n{source}\n\n{helpers}\n'
        truth["modules"][u["module"]] = {"template": u["template"], "fn": u["fields"]["fn"],
                                        "oracle_tests": oracle, "mutants": muts,
                                        "unit_chars": len(files[f"lib/{u['module']}.py"]) + 1500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


def _grade_module(ws, pristine, mod, info):
    test_path = Path(ws) / "tests" / f"test_{mod}.py"
    if not test_path.exists():
        return 0.0, "missing"
    tests = test_path.read_text()
    if any(tok in tests for tok in FORBIDDEN_IN_TESTS):
        return 0.0, "reads source"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for rel in ("lib/__init__.py", "tests/__init__.py", "tests/conftest.py", "pytest.ini"):
            write(tmp, rel, pristine[rel])
        write(tmp, f"tests/test_{mod}.py", tests)
        original = pristine[f"lib/{mod}.py"]
        write(tmp, f"lib/{mod}.py", original)
        ok, _ = run_pytest(tmp, f"tests/test_{mod}.py", timeout=60)
        if not ok:
            return 0.0, "fails on the real code"
        killed = 0
        for a, b in info["mutants"]:
            write(tmp, f"lib/{mod}.py", original.replace(a, b, 1))
            ok, _ = run_pytest(tmp, f"tests/test_{mod}.py", timeout=60)
            killed += not ok
        return killed / len(info["mutants"]), f"killed {killed}/{len(info['mutants'])}"


def grade(seed, workspace):
    """Per module: the fraction of planted mutants the agent's tests kill, or 0
    if the tests fail on the real code or read the source. Reward is the mean."""
    truth, pristine = generate(seed)
    per = {mod: _grade_module(workspace, pristine, mod, info) for mod, info in truth["modules"].items()}
    return {"reward": round(sum(s for s, _ in per.values()) / len(per), 4),
            "modules": {m: {"score": round(s, 3), "why": w} for m, (s, w) in per.items()}}


def solve(seed, workspace):
    truth, _ = generate(seed)
    for mod, info in truth["modules"].items():
        write(Path(workspace) / "tests", f"test_{mod}.py", info["oracle_tests"])


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [m["unit_chars"] for m in t["modules"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": 500}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Write the missing tests

Nothing under `/workspace/lib/` has tests. For every module `lib/<name>.py`,
write `tests/test_<name>.py` (pytest) for its public function. Each public
function's docstring is its specification.

Your tests should pass against the code as it is and fail if the behaviour
the docstring specifies ever changes. Test behaviour through the function
itself; do not read or fingerprint the source.

Run them with `cd /workspace && python -m pytest`. Do not modify `lib/`.
"""

META = {
    "unit": "module", "kind": "test writing", "domain": "unit testing", "output_tokens": 2000, "needs_pytest": True,
    "failure_mode": "writing tests from a spec (graded by mutation, not by coverage)",
    "deliverable": "`tests/test_<module>.py` for each of the 40 modules",
    "grading": "Per module: the fraction of planted mutants (one-line changes that each break one "
               "sentence of the docstring) that the agent's tests kill; 0 if the tests fail on the real "
               "code or read the source. Reward is the mean.",
    "per_unit": "read the function and its docstring, enumerate every edge and error case the docstring "
                "states, and write a test that pins each",
    "traps": [
        "**Smoke tests score near zero.** Mutants break boundaries (`<` vs `<=`), rounding modes, "
        "error paths and ordering rules, which only edge-case tests catch.",
        "**Variants differ subtly** (lowercase vs uppercase numerals, `-` vs `_` separators, 2 vs 3 "
        "decimal places), so tests copied from one module fail on its sibling.",
        "**Reading the source is refused**, so fingerprinting cannot stand in for testing.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
