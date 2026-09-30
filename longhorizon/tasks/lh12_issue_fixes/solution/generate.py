#!/usr/bin/env python3
"""LH12 -- work through a 40-issue backlog: fix, close, or link each one.

shop/ has 36 pricing and billing modules; docs/spec.md states each function's
rules. issues/ holds 40 bug reports, each with an input, what the reporter
expected, and what they got. They are not all bugs:

- **bug** -- the code breaks the spec. Fix it; a hidden spec test must pass.
- **duplicate** -- the same defect as an earlier issue, reported with a
  different input. Link it (`duplicate_of`), do not fix twice.
- **not_a_bug** -- the code does what the spec says; the reporter misread it
  (half-up vs banker's rounding, a grace period, a cap). Close it and leave the
  code alone: "fixing" it breaks the spec test.
- **cannot_reproduce** -- filed against an old version; the current code
  already gives the expected result.

Every symptom in every issue is computed by running the real and the defective
code, so each claim in the tracker is exactly true of the version it names.

    python3 lh12_issue_fixes.py --seed 1 --out /fixture
"""

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import filler_function, load_json_answer, rng_for, run_pytest, standard_main, write  # noqa: E402

N_MODULES = 36
MIX = {"bug": 22, "duplicate": 6, "not_a_bug": 8, "cannot_reproduce": 4}  # 40 issues

# template: (spec sentence, source, spec tests, bug mutants, misreadings, inputs)
# `misreadings` are changes a reporter might BELIEVE in; the code is right.
T = {
    "tiered_discount": (
        "Orders of 100.00 or more get 5% off; 500.00 or more get 12% off. The threshold amounts "
        "themselves qualify. The result is rounded to cents, half up.",
        '''from decimal import ROUND_HALF_UP, Decimal


def {fn}(total):
    total = Decimal(str(total))
    rate = Decimal("0.12") if total >= 500 else Decimal("0.05") if total >= 100 else Decimal(0)
    return (total * (1 - rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
''',
        ['assert {fn}("99.99") == Decimal("99.99")', 'assert {fn}("100") == Decimal("95.00")',
         'assert {fn}("500") == Decimal("440.00")', 'assert {fn}("250.10") == Decimal("237.60")'],
        [("total >= 500", "total > 500"), ("total >= 100", "total > 100"), ('Decimal("0.12")', 'Decimal("0.21")')],
        [("rounding=ROUND_HALF_UP", 'rounding="ROUND_DOWN"'), ('Decimal("0.05") if', 'Decimal("0.10") if')],
        ['"100"', '"500"', '"250.10"', '"99.99"', '"1000"', '"100.01"', '"123.45"']),
    "shipping": (
        "Shipping is 4.00 for parcels up to and including 1 kg, then 1.50 per started extra kg, "
        "capped at 30.00. Weight must be positive; otherwise ValueError.",
        '''import math


def {fn}(weight_kg):
    if weight_kg <= 0:
        raise ValueError(weight_kg)
    extra = max(0, math.ceil(weight_kg - 1))
    return min(4.00 + 1.50 * extra, 30.00)
''',
        ['assert {fn}(1) == 4.0', 'assert {fn}(1.2) == 5.5', 'assert {fn}(3) == 7.0', 'assert {fn}(40) == 30.0',
         'import pytest\n    with pytest.raises(ValueError): {fn}(0)'],
        [("math.ceil(weight_kg - 1)", "math.floor(weight_kg - 1)"), ("min(4.00 + 1.50 * extra, 30.00)", "4.00 + 1.50 * extra"),
         ("if weight_kg <= 0:", "if weight_kg < 0:")],
        [("math.ceil(weight_kg - 1)", "round(weight_kg - 1)"), ("30.00)", "25.00)")],
        ["1.2", "3", "40", "2.5", "1.01", "18", "0.5", "0"]),
    "late_fee": (
        "Invoices paid more than 5 days late pay 2.00 per day late, counting from the first day "
        "(so 6 days late costs 12.00), capped at 50.00. Paying 5 or fewer days late costs nothing.",
        '''def {fn}(days_late):
    if days_late <= 5:
        return 0.0
    return min(2.00 * days_late, 50.00)
''',
        ['assert {fn}(5) == 0.0', 'assert {fn}(6) == 12.0', 'assert {fn}(10) == 20.0', 'assert {fn}(40) == 50.0',
         'assert {fn}(0) == 0.0'],
        [("if days_late <= 5:", "if days_late < 5:"), ("2.00 * days_late", "2.00 * (days_late - 5)"),
         ("min(2.00 * days_late, 50.00)", "2.00 * days_late")],
        [("2.00 * days_late", "2.00 * (days_late - 5)"), ("50.00)", "30.00)")],
        ["6", "10", "40", "5", "7", "26", "3"]),
    "proration": (
        "A plan change mid-period refunds the unused share: price * (days_in_period - days_used) / "
        "days_in_period, rounded to cents half up. days_used may not exceed days_in_period (ValueError).",
        '''from decimal import ROUND_HALF_UP, Decimal


def {fn}(price, days_used, days_in_period):
    if days_used > days_in_period:
        raise ValueError(days_used)
    unused = Decimal(days_in_period - days_used) / Decimal(days_in_period)
    return (Decimal(str(price)) * unused).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
''',
        ['assert {fn}("30", 10, 30) == Decimal("20.00")', 'assert {fn}("10", 0, 31) == Decimal("10.00")',
         'assert {fn}("9.99", 7, 30) == Decimal("7.66")', 'assert {fn}("19.99", 2, 3) == Decimal("6.66")',
         'import pytest\n    with pytest.raises(ValueError): {fn}("10", 31, 30)'],
        [("days_in_period - days_used", "days_used"), ("if days_used > days_in_period:", "if days_used > days_in_period + 1:"),
         ("rounding=ROUND_HALF_UP", "rounding=\"ROUND_DOWN\"")],
        [("Decimal(days_in_period)", "Decimal(30)"), ("rounding=ROUND_HALF_UP", "rounding=\"ROUND_UP\"")],
        ['"30", 10, 30', '"9.99", 7, 30', '"10", 0, 31', '"50", 29, 31', '"12.34", 3, 28', '"19.99", 2, 3', '"10", 31, 30']),
    "loyalty": (
        "Members earn 1 point per whole currency unit spent, times their tier multiplier (silver 1, "
        "gold 2, platinum 3); points per order are capped at 1000. Unknown tiers raise KeyError.",
        '''_MULT = {{"silver": 1, "gold": 2, "platinum": 3}}


def {fn}(amount, tier):
    return min(int(amount) * _MULT[tier], 1000)
''',
        ['assert {fn}(99.99, "silver") == 99', 'assert {fn}(120, "gold") == 240', 'assert {fn}(100, "platinum") == 300', 'assert {fn}(500, "platinum") == 1000',
         'import pytest\n    with pytest.raises(KeyError): {fn}(10, "bronze")'],
        [("int(amount)", "round(amount)"), ('"platinum": 3', '"platinum": 2'), ("min(int(amount) * _MULT[tier], 1000)", "int(amount) * _MULT[tier]")],
        [("int(amount)", "round(amount)"), (", 1000)", ", 2000)")],
        ['99.99, "silver"', '120, "gold"', '500, "platinum"', '10.5, "gold"', '400, "platinum"', '700, "silver"']),
    "coupon": (
        "A percentage coupon takes pct% off; a fixed coupon takes a fixed amount off. Either applies "
        "only when the total is at least min_spend, and never takes the total below 0.00.",
        '''def {fn}(total, kind, value, min_spend=0):
    if total < min_spend:
        return round(total, 2)
    off = total * value / 100 if kind == "pct" else value
    return round(max(total - off, 0.0), 2)
''',
        ['assert {fn}(80, "pct", 10) == 72.0', 'assert {fn}(30, "fixed", 50) == 0.0',
         'assert {fn}(49, "fixed", 5, min_spend=50) == 49.0', 'assert {fn}(50, "fixed", 5, min_spend=50) == 45.0'],
        [("if total < min_spend:", "if total <= min_spend:"), ("max(total - off, 0.0)", "total - off"),
         ("total * value / 100", "value / 100")],
        [("if total < min_spend:", "if total < 0:"), ("max(total - off, 0.0)", "max(total - off, 1.0)")],
        ['80, "pct", 10', '30, "fixed", 50', '50, "fixed", 5, 50', '49, "fixed", 5, 50', '200, "pct", 25', '10, "fixed", 10']),
    "tax": (
        "Tax is amount * rate for the region (DE 0.19, FR 0.20, UK 0.20, US 0.0); items in the "
        "`food` category pay half the regional rate. Rounded to cents, half up.",
        '''from decimal import ROUND_HALF_UP, Decimal

_RATES = {{"DE": Decimal("0.19"), "FR": Decimal("0.20"), "UK": Decimal("0.20"), "US": Decimal("0")}}


def {fn}(amount, region, category="general"):
    rate = _RATES[region] / 2 if category == "food" else _RATES[region]
    return (Decimal(str(amount)) * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
''',
        ['assert {fn}(100, "DE") == Decimal("19.00")', 'assert {fn}(100, "DE", "food") == Decimal("9.50")',
         'assert {fn}(10.05, "FR") == Decimal("2.01")', 'assert {fn}(50, "US") == Decimal("0.00")',
         'assert {fn}(33.33, "UK") == Decimal("6.67")'],
        [('"DE": Decimal("0.19")', '"DE": Decimal("0.16")'), ("_RATES[region] / 2", "_RATES[region]"),
         ("rounding=ROUND_HALF_UP", "rounding=\"ROUND_DOWN\"")],
        [('_RATES[region] / 2 if category == "food"', '_RATES[region] * 0 if category == "food"'),
         ('"UK": Decimal("0.20")', '"UK": Decimal("0.175")')],
        ['100, "DE"', '100, "DE", "food"', '10.05, "FR"', '33.33, "UK"', '12.5, "DE", "food"', '80, "FR", "food"']),
    "refund": (
        "A return refunds the price minus a 15% restocking fee, except that items returned within "
        "14 days (inclusive) pay no fee. Opened software is never refundable (0.00).",
        '''def {fn}(price, days_since_purchase, opened_software=False):
    if opened_software:
        return 0.0
    if days_since_purchase <= 14:
        return round(price, 2)
    return round(price * 0.85, 2)
''',
        ['assert {fn}(100, 14) == 100.0', 'assert {fn}(100, 15) == 85.0', 'assert {fn}(60, 3, True) == 0.0',
         'assert {fn}(19.99, 30) == 16.99'],
        [("days_since_purchase <= 14", "days_since_purchase < 14"), ("price * 0.85", "price * 0.8"),
         ("if opened_software:\n        return 0.0", "if opened_software:\n        pass")],
        [("days_since_purchase <= 14", "days_since_purchase <= 30"), ("price * 0.85", "price * 0.9")],
        ["100, 14", "100, 15", "60, 3, True", "19.99, 30", "250, 20", "80, 1"]),
    "fx": (
        "Convert with the given rate and round to the target currency's minor unit: 2 decimals, "
        "except JPY and KRW which have 0. Rounding is half to even.",
        '''from decimal import ROUND_HALF_EVEN, Decimal

_ZERO_DECIMAL = {{"JPY", "KRW"}}


def {fn}(amount, rate, currency):
    exp = Decimal(1) if currency in _ZERO_DECIMAL else Decimal("0.01")
    return (Decimal(str(amount)) * Decimal(str(rate))).quantize(exp, rounding=ROUND_HALF_EVEN)
''',
        ['assert {fn}(10, "1.1", "USD") == Decimal("11.00")', 'assert {fn}(1, "150.5", "JPY") == Decimal("150")',
         'assert {fn}(1, "151.5", "JPY") == Decimal("152")', 'assert {fn}("0.125", 1, "EUR") == Decimal("0.12")',
         'assert {fn}(1, "1350.5", "KRW") == Decimal("1350")'],
        [('{{"JPY", "KRW"}}', '{{"JPY"}}'), ("rounding=ROUND_HALF_EVEN", "rounding=\"ROUND_HALF_UP\""),
         ('Decimal(1) if', 'Decimal("0.1") if')],
        [("rounding=ROUND_HALF_EVEN", "rounding=\"ROUND_HALF_UP\""), ('{{"JPY", "KRW"}}', 'set()')],
        ['1, "150.5", "JPY"', '"0.125", 1, "EUR"', '1, "1350.5", "KRW"', '10, "1.1", "USD"', '"2.345", 1, "GBP"', '3, "0.5", "JPY"']),
    "bundle": (
        "Buying 3 or more units of the same SKU makes every third unit free (6 units: pay for 4). "
        "Unit prices are per SKU; quantities of 0 are ignored.",
        '''def {fn}(unit_price, quantity):
    if quantity <= 0:
        return 0.0
    free = quantity // 3
    return round(unit_price * (quantity - free), 2)
''',
        ['assert {fn}(10, 2) == 20.0', 'assert {fn}(10, 3) == 20.0', 'assert {fn}(10, 6) == 40.0',
         'assert {fn}(10, 7) == 50.0', 'assert {fn}(10, 0) == 0.0'],
        [("quantity // 3", "quantity // 4"), ("quantity // 3", "(quantity - 1) // 3"), ("free = quantity // 3", "free = quantity // 3 if quantity > 3 else 0")],
        [("quantity // 3", "quantity // 2"), ("quantity // 3", "(quantity // 3) * 2")],
        ["10, 3", "10, 6", "10, 7", "10, 2", "4.5, 9", "10, 4"]),
}
TEMPLATE_NAMES = list(T)


def _fmt(text, fn):
    return text.replace("{fn}", fn).replace("{{", "{").replace("}}", "}")


def _load(source, fn):
    ns = {}
    exec(source, ns)  # noqa: S102 -- generator-only, on code it wrote itself
    return ns[fn]


def _call(f, args):
    try:
        return repr(eval(f"__f({args})", {"__f": f}))  # noqa: S307
    except Exception as e:  # noqa: BLE001 -- an exception IS the observed behaviour
        return f"raises {type(e).__name__}"


def _diff_inputs(src_a, src_b, fn, inputs):
    fa, fb = _load(src_a, fn), _load(src_b, fn)
    return [(i, _call(fa, i), _call(fb, i)) for i in inputs if _call(fa, i) != _call(fb, i)]


def plan(seed):
    rng = rng_for(seed, "plan")
    modules = []
    for i in range(N_MODULES):
        tpl = TEMPLATE_NAMES[i % len(TEMPLATE_NAMES)]
        modules.append({"module": f"{tpl}_{i:02d}", "template": tpl,
                        "fn": f"{rng.choice(['calc', 'compute', 'price', 'apply'])}_{tpl}"})
    rng.shuffle(modules)
    kinds = sum(([k] * v for k, v in MIX.items() if k != "duplicate"), [])
    rng.shuffle(kinds)
    # One issue per module for bug / not_a_bug / cannot_reproduce, then duplicates of bugs.
    assert len(kinds) <= len(modules)
    issues = []
    for mod, kind in zip(modules, kinds):
        issues.append({"kind": kind, **mod})
    bugs = [x for x in issues if x["kind"] == "bug"]
    for original in rng.sample(bugs, MIX["duplicate"]):
        issues.append({"kind": "duplicate", **{k: original[k] for k in ("module", "template", "fn")},
                       "of_module": original["module"]})
    rng.shuffle(issues)
    for n, iss in enumerate(issues):
        iss["id"] = f"ISSUE-{101 + n}"
    return modules, issues


def generate(seed, out=None):
    rng = rng_for(seed, "content")
    modules, issues = plan(seed)
    by_module = {}
    for iss in issues:
        by_module.setdefault(iss["module"], []).append(iss)
    files = {"shop/__init__.py": "", "tests/__init__.py": "",
             "pytest.ini": "[pytest]\naddopts = -q -p no:cacheprovider --import-mode=importlib\n",
             "tests/conftest.py": "import sys\nfrom pathlib import Path\n\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n"}
    spec = ["# Pricing and billing rules", "", "Each module under `shop/` implements one rule. This document is "
            "authoritative: where an issue and this spec disagree, the spec wins.", ""]
    truth = {"seed": seed, "issues": {}, "modules": {}}
    bug_of = {}
    for mod in sorted(modules, key=lambda m: m["module"]):
        sentence, src, tests, bugs, misreads, inputs = T[mod["template"]]
        correct = _fmt(src, mod["fn"])
        mod_issues = by_module.get(mod["module"], [])
        shipped = correct
        if any(i["kind"] == "bug" for i in mod_issues):
            a, b = bugs[rng.randrange(len(bugs))]
            shipped = correct.replace(_fmt(a, mod["fn"]), _fmt(b, mod["fn"]), 1)
            bug_of[mod["module"]] = shipped
        filler = "\n\n".join(filler_function(rng) for _ in range(rng.randint(3, 6)))
        header = f'"""{mod["module"]}: see docs/spec.md."""\n\n'
        files[f"shop/{mod['module']}.py"] = f"{header}{shipped}\n\n{filler}\n"
        spec += [f"## `shop/{mod['module']}.py` -- `{mod['fn']}`", "", sentence, ""]
        test_body = "\n\n".join(f"def test_{k}():\n    " + _fmt(t, mod["fn"]) for k, t in enumerate(tests))
        truth["modules"][mod["module"]] = {
            "correct": correct,
            "file_correct": f"{header}{correct}\n\n{filler}\n",
            "spec_tests": f"from decimal import Decimal\n\nfrom shop.{mod['module']} import {mod['fn']}\n\n\n{test_body}\n",
        }

    first_bug_issue = {}
    for iss in sorted(issues, key=lambda x: x["id"]):
        if iss["kind"] == "bug":
            first_bug_issue[iss["module"]] = iss["id"]
    for iss in issues:
        _, src, _, bugs, misreads, inputs = T[iss["template"]]
        correct = truth["modules"][iss["module"]]["correct"]
        fn = iss["fn"]
        version = "3.1.0"
        if iss["kind"] in ("bug", "duplicate"):
            diffs = _diff_inputs(correct, bug_of[iss["module"]], fn, inputs)
            args, expected, actual = diffs[0 if iss["kind"] == "bug" else min(1, len(diffs) - 1)]
        elif iss["kind"] == "not_a_bug":
            a, b = misreads[rng.randrange(len(misreads))]
            believed = correct.replace(_fmt(a, fn), _fmt(b, fn), 1)
            args, actual, expected = _diff_inputs(correct, believed, fn, inputs)[0]
        else:  # cannot_reproduce: the reported defect is not in the current code
            a, b = bugs[rng.randrange(len(bugs))]
            old = correct.replace(_fmt(a, fn), _fmt(b, fn), 1)
            args, expected, actual = _diff_inputs(correct, old, fn, inputs)[0]
            version = rng.choice(["2.4.0", "2.7.1", "2.9.3"])
        title = rng.choice(["Wrong result from", "Unexpected value in", "Incorrect output:", "Bug in"])
        files[f"issues/{iss['id']}.md"] = (
            f"# {iss['id']}: {title} `{fn}`\n\n**Reported against:** shop {version}\n\n"
            f"Calling `{fn}({args})` (in `shop/{iss['module']}.py`):\n\n"
            f"- expected: `{expected}`\n- actual: `{actual}`\n\n"
            f"{rng.choice(['Customer noticed this on their invoice.', 'Found while reconciling last month.', 'Support escalated this.', 'Seen in the nightly report.'])}\n")
        truth["issues"][iss["id"]] = {
            "kind": "fixed" if iss["kind"] == "bug" else iss["kind"], "module": iss["module"],
            "duplicate_of": first_bug_issue.get(iss["module"]) if iss["kind"] == "duplicate" else None,
            "unit_chars": len(files[f"shop/{iss['module']}.py"]) + 1500,
        }
    files["docs/spec.md"] = "\n".join(spec) + "\n"
    files["VERSION"] = "3.1.0\n"
    truth["shared_chars"] = len(files["docs/spec.md"]) // 4
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth, files


def _module_meets_spec(ws, pristine, truth, module):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for rel in ("shop/__init__.py", "tests/__init__.py", "tests/conftest.py", "pytest.ini"):
            write(tmp, rel, pristine[rel])
        src = Path(ws) / "shop" / f"{module}.py"
        if not src.exists():
            return False
        shutil.copy(src, tmp / "shop" / f"{module}.py")
        write(tmp, "tests/test_spec.py", truth["modules"][module]["spec_tests"])
        return run_pytest(tmp, "tests/test_spec.py", timeout=60)[0]


def grade(seed, workspace):
    """Per issue: the resolution in triage.json must be right (and a duplicate
    must name the right original), AND the module it concerns must meet its spec
    afterwards -- fixed if it was broken, untouched in behaviour if it was not.
    Reward is the mean over issues."""
    truth, pristine = generate(seed)
    ws = Path(workspace)
    triage = load_json_answer(ws / "triage.json")
    spec_ok = {m: _module_meets_spec(ws, pristine, truth, m) for m in {i["module"] for i in truth["issues"].values()}}
    per = {}
    for iid, t in truth["issues"].items():
        got = triage.get(iid) if isinstance(triage.get(iid), dict) else {}
        ok = got.get("resolution") == t["kind"] and spec_ok[t["module"]]
        if t["kind"] == "duplicate":
            ok = ok and got.get("duplicate_of") == t["duplicate_of"]
        per[iid] = float(ok)
    return {"reward": round(sum(per.values()) / len(per), 4), "issues": per,
            "modules_meeting_spec": sum(spec_ok.values()), "of": len(spec_ok)}


def solve(seed, workspace):
    """The reference: every module as the spec defines it, and the right triage."""
    import json
    truth, _ = generate(seed)
    ws = Path(workspace)
    for module, info in truth["modules"].items():
        write(ws / "shop", f"{module}.py", info["file_correct"])
    triage = {iid: {"resolution": t["kind"], **({"duplicate_of": t["duplicate_of"]} if t["duplicate_of"] else {})}
              for iid, t in truth["issues"].items()}
    write(ws, "triage.json", json.dumps(triage, indent=2))


def shape(seed):
    t, _ = generate(seed)
    return {"unit_chars": [i["unit_chars"] for i in t["issues"].values()],
            "judgement_turns": 6, "orchestration_turns": 12, "shared_chars": t["shared_chars"]}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Clear the billing bug backlog

`issues/` holds the open bug reports against `shop/`. `docs/spec.md` is the
authority on how every function must behave.

Go through every issue. Fix the ones that are real defects. Close the ones that
are not, and link duplicates to the earlier issue for the same defect. Do not
change behaviour the spec requires, even if an issue asks for it.

Record the outcome of every issue in `/workspace/triage.json`:

```json
{"ISSUE-NNN": {"resolution": "fixed" | "duplicate" | "not_a_bug" | "cannot_reproduce",
               "duplicate_of": "ISSUE-NNN (duplicates only)"}}
```
"""

META = {
    "unit": "issue", "kind": "bug fixes", "domain": "issue tracker", "output_tokens": 1800, "needs_pytest": True,
    "failure_mode": "triage judgement over a mixed backlog: bug, duplicate, misreading, stale report",
    "deliverable": "code fixes under `shop/` and `/workspace/triage.json`",
    "grading": "Per issue: the resolution is right (duplicates must name the original), AND the module "
               "meets a hidden spec test afterwards. Reward is the mean.",
    "per_unit": "reproduce the reported call, compare with the spec, decide which of four outcomes applies, "
                "and fix the code only if it is really broken",
    "traps": [
        "**Not every report is a bug.** A fifth of reporters misread the spec (half-up vs banker's "
        "rounding, a grace period, a cap). Changing the code to match them fails the spec test.",
        "**Stale reports.** Some issues were filed against an old version; the current code already "
        "gives the expected value.",
        "**Duplicates** report the same defect with a different input; they must be linked to the "
        "earlier issue, which requires comparing root causes, not symptoms.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
