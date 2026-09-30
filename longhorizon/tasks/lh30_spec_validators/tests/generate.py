#!/usr/bin/env python3
"""LH30 -- implement 48 identifier validators from their written specifications.

specs/<format>.md each define one identifier used by a partner system: tax
numbers, account numbers, personal ids, postal codes, plates. The deliverable
is validators/<format>.py with `is_valid(text) -> bool`, graded on hidden
strings: valid ones, and near misses -- a wrong check character, 30 February, a
forbidden letter, a separator in the wrong place.

The formats are invented, so no library implements them, and each spec has
its own parameters: which letters, which weights, which modulus, what a check
value of 10 becomes, which positions may hold a separator.

    python3 lh30_spec_validators.py --seed 1 --out /fixture
"""

import datetime as dt
import json
import string
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_FORMATS = 48
KINDS = ["weighted", "mod97", "dated", "pattern", "luhn_sep"]


# ------------------------------------------------------------------ the checks

def weighted_check(digits, weights, modulus, ten_as):
    total = sum(int(d) * weights[i % len(weights)] for i, d in enumerate(digits))
    r = total % modulus
    v = (modulus - r) % modulus
    return ten_as if v == 10 else str(v % 10)


def mod97_check(body):
    """ISO 7064 mod 97-10 over letters (A=10..Z=35) and digits, as IBAN does."""
    num = "".join(str(int(c, 36)) for c in body + "00")
    return f"{98 - int(num) % 97:02d}"


def luhn_ok(digits):
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            d -= 9 if d > 9 else 0
        total += d
    return total % 10 == 0


def luhn_digit(body):
    for d in "0123456789":
        if luhn_ok(body + d):
            return d


def validate(p, s):
    """The reference validator for a format with parameters p."""
    k = p["kind"]
    if not isinstance(s, str):
        return False
    if k == "weighted":
        n = len(p["prefixes"][0])
        if len(s) != n + p["digits"] + 1 or s[:n] not in p["prefixes"] or not s[n:-1].isdigit():
            return False
        return s[-1] == weighted_check(s[n:-1], p["weights"], p["modulus"], p["ten_as"])
    if k == "mod97":
        if len(s) != 2 + 2 + p["body_len"] or s[:2] != p["country"] or not s[2:4].isdigit():
            return False
        body = s[4:]
        if not all(c in string.digits + string.ascii_uppercase for c in body):
            return False
        return mod97_check(body + p["country"]) == s[2:4]
    if k == "dated":
        if len(s) != 6 + 1 + p["serial"] + 1 or s[6] != p["sep"] or not (s[:6] + s[7:]).isdigit():
            return False
        yy, mm, dd = int(s[:2]), int(s[2:4]), int(s[4:6])
        year = (1900 if yy >= p["pivot"] else 2000) + yy
        try:
            dt.date(year, mm, dd)
        except ValueError:
            return False
        return luhn_ok(s[:6] + s[7:])
    if k == "pattern":
        parts = s.split(" ")
        if len(parts) != 2 or len(parts[0]) != p["left"] or len(parts[1]) != p["right"]:
            return False
        if not parts[0].isdigit() or parts[0][0] == "0":
            return False
        return parts[1].isalpha() and parts[1].isupper() and not set(parts[1]) & set(p["forbidden"]) \
            and parts[1] not in p["reserved"]
    # luhn_sep
    raw = s
    for pos in sorted(p["sep_positions"], reverse=True):
        if len(raw) > pos and raw[pos] == "-":
            raw = raw[:pos] + raw[pos + 1:]
    return raw.isdigit() and len(raw) == p["length"] and luhn_ok(raw)


def make_valid(p, rng):
    k = p["kind"]
    if k == "weighted":
        body = "".join(rng.choice(string.digits) for _ in range(p["digits"]))
        return rng.choice(p["prefixes"]) + body + weighted_check(body, p["weights"], p["modulus"], p["ten_as"])
    if k == "mod97":
        body = "".join(rng.choice(string.digits + string.ascii_uppercase) for _ in range(p["body_len"]))
        return p["country"] + mod97_check(body + p["country"]) + body
    if k == "dated":
        while True:
            d = dt.date(rng.randint(1950, 2024), rng.randint(1, 12), rng.randint(1, 28 if rng.random() < 0.9 else 29))
            yy = d.year % 100
            if (d.year < 2000) == (yy >= p["pivot"]):
                break
        serial = "".join(rng.choice(string.digits) for _ in range(p["serial"]))
        body = d.strftime("%y%m%d") + serial
        return f"{body[:6]}{p['sep']}{body[6:]}{luhn_digit(body)}"
    if k == "pattern":
        left = str(rng.randint(1, 9)) + "".join(rng.choice(string.digits) for _ in range(p["left"] - 1))
        letters = [c for c in string.ascii_uppercase if c not in p["forbidden"]]
        while True:
            right = "".join(rng.choice(letters) for _ in range(p["right"]))
            if right not in p["reserved"]:
                return f"{left} {right}"
    body = "".join(rng.choice(string.digits) for _ in range(p["length"] - 1))
    raw = body + luhn_digit(body)
    out = raw
    if rng.random() < 0.6:
        for pos in sorted(p["sep_positions"]):
            out = out[:pos] + "-" + out[pos:]
    return out


def near_misses(p, valid, rng):
    out = []
    s = valid
    # flip the last character
    last = s[-1]
    alts = [c for c in (string.digits + "X") if c != last]
    out.append(s[:-1] + rng.choice(alts))
    # swap two adjacent digits in the middle
    i = len(s) // 2
    if s[i].isdigit() and s[i + 1].isdigit() and s[i] != s[i + 1]:
        out.append(s[:i] + s[i + 1] + s[i] + s[i + 2:])
    if p["kind"] == "dated":
        out.append(s[:2] + "02" + "30" + s[6:])
        out.append(s[:2] + "13" + s[4:])
    if p["kind"] == "pattern":
        out.append(s[:-1] + rng.choice(p["forbidden"]))
        out.append("0" + s[1:])
        out.append(s.split(" ")[0] + " " + p["reserved"][0])
        out.append(s.replace(" ", ""))
    if p["kind"] == "luhn_sep":
        raw = s.replace("-", "")
        out.append(raw[:3] + "-" + raw[3:])
    if p["kind"] == "weighted":
        out.append(rng.choice([x for x in "ABCDEFGH" if x * len(p["prefixes"][0]) not in p["prefixes"]]) * len(p["prefixes"][0]) + s[len(p["prefixes"][0]):])
    if p["kind"] == "mod97":
        out.append(s.lower())
    return out


def params(rng, kind):
    if kind == "weighted":
        n = rng.choice([1, 2])
        return {"kind": kind, "prefixes": sorted({"".join(rng.choice(string.ascii_uppercase) for _ in range(n)) for _ in range(4)}),
                "digits": rng.choice([7, 8, 9]), "weights": rng.sample(range(2, 10), rng.randint(3, 6)),
                "modulus": 11, "ten_as": rng.choice(["X", "0", "K"])}
    if kind == "mod97":
        return {"kind": kind, "country": rng.choice(["AV", "BR", "CV", "DK", "ES", "FL"]), "body_len": rng.choice([10, 12, 14])}
    if kind == "dated":
        return {"kind": kind, "serial": rng.choice([3, 4]), "sep": rng.choice(["-", "+", "/"]), "pivot": rng.choice([25, 30, 40])}
    if kind == "pattern":
        return {"kind": kind, "left": 4, "right": 2, "forbidden": rng.sample(list("IOQUWYZ"), 3),
                "reserved": ["SA", "SD", "SS"] if rng.random() < 0.5 else ["AA", "XX"]}
    return {"kind": kind, "length": rng.choice([12, 14, 16]), "sep_positions": sorted(rng.sample([4, 8, 10], 2))}


def spec_md(name, p):
    k = p["kind"]
    if k == "weighted":
        body = (f"{len(p['prefixes'][0])}-letter prefix, one of: {', '.join(p['prefixes'])}; then {p['digits']} digits; "
                f"then one check character. Multiply the digits (left to right) by the weights "
                f"{', '.join(map(str, p['weights']))} (repeating the weights as needed) and sum. The check value is "
                f"(11 - sum mod 11) mod 11; a value of 10 is written `{p['ten_as']}`, otherwise the digit.")
    elif k == "mod97":
        body = (f"`{p['country']}`, then two check digits, then {p['body_len']} characters (digits or upper-case "
                f"letters). The check digits are computed as for an IBAN: move `{p['country']}00` to the end of the "
                f"body, replace each letter by its number (A=10 ... Z=35), take the whole number mod 97, and "
                f"subtract from 98 (two digits, with a leading zero).")
    elif k == "dated":
        body = (f"`YYMMDD{p['sep']}` then a {p['serial']}-digit serial and one check digit. YYMMDD is the holder's "
                f"date of birth and must be a real date: years `{p['pivot']:02d}`-`99` are 19xx, `00`-`{p['pivot'] - 1:02d}` "
                f"are 20xx. The check digit is chosen so that all the digits together (without `{p['sep']}`) "
                f"pass the Luhn check.")
    elif k == "pattern":
        body = (f"{p['left']} digits (the first not 0), one space, {p['right']} upper-case letters. The letters "
                f"{', '.join(p['forbidden'])} are never used, and the letter pairs {', '.join(p['reserved'])} are reserved "
                f"and never issued.")
    else:
        body = (f"{p['length']} digits passing the Luhn check. For readability a hyphen may appear after the first "
                f"{p['sep_positions'][0]} digits and/or after the first {p['sep_positions'][1]} digits; no other "
                f"separators are allowed.")
    return f"# {name}\n\n{body}\n"


def plan(seed):
    rng = rng_for(seed, "plan")
    things = ["tax-number", "account-id", "member-id", "postal-code", "plate", "policy-number", "citizen-id", "vat-id"]
    places = ["alvoria", "brisca", "corvel", "drenmark", "esperi", "faloria", "gantis", "halvenn"]
    names = rng.sample([f"{pl}-{th}" for pl in places for th in things], N_FORMATS)
    return [(name, params(rng_for(seed, "fmt", name), KINDS[i % len(KINDS)])) for i, name in enumerate(names)]


def cases(seed, name, p):
    rng = rng_for(seed, "cases", name)
    out = []
    for _ in range(16):  # one valid string and one near miss each: balanced
        v = make_valid(p, rng)
        out.append(v)
        out.append(rng.choice(near_misses(p, v, rng)))
    return [(c, validate(p, c)) for c in dict.fromkeys(out)]


def generate(seed, out=None):
    files = {}
    truth = {"seed": seed, "formats": {}}
    for name, p in plan(seed):
        files[f"specs/{name}.md"] = spec_md(name, p)
        rng = rng_for(seed, "examples", name)
        ex = [make_valid(p, rng) for _ in range(3)]
        files[f"specs/{name}.md"] += "\nValid examples: " + ", ".join(f"`{e}`" for e in ex) + "\n"
        truth["formats"][name] = {"params": p, "unit_chars": 3500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
        (Path(out) / "workspace" / "validators").mkdir(parents=True, exist_ok=True)
    return truth


RUNNER = """import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("v", sys.argv[1]); mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print(json.dumps([bool(mod.is_valid(s)) for s in json.load(open(sys.argv[2]))]))
"""


def grade(seed, workspace):
    """Per format, all or nothing: every hidden string (valid ones and near
    misses) classified correctly. Reward is the mean."""
    truth = generate(seed)
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / "run.py"
        runner.write_text(RUNNER)
        for name, t in truth["formats"].items():
            path = Path(workspace) / "validators" / f"{name}.py"
            if not path.exists():
                per[name] = 0.0
                continue
            cs = cases(seed, name, t["params"])
            inp = Path(tmp) / "in.json"
            inp.write_text(json.dumps([c for c, _ in cs]))
            try:
                run = subprocess.run([sys.executable, str(runner), str(path), str(inp)], capture_output=True,
                                     text=True, timeout=30)
                got = json.loads(run.stdout) if run.returncode == 0 else []
            except (subprocess.TimeoutExpired, ValueError):
                got = []
            per[name] = float(got == [w for _, w in cs])
    return {"reward": round(sum(per.values()) / len(per), 4), "formats": per}


ORACLE = '''"""Reference validator (generated)."""
import importlib.util
from pathlib import Path

_ref = Path(__file__).resolve().parent / "_ref" / "generate.py"
_spec = importlib.util.spec_from_file_location("gen", _ref)
_gen = importlib.util.module_from_spec(_spec)
import sys
sys.path.insert(0, str(_ref.parent))
_spec.loader.exec_module(_gen)
PARAMS = {params!r}


def is_valid(text):
    return _gen.validate(PARAMS, text)
'''


def solve(seed, workspace):
    here = Path(__file__).resolve().parent
    ref = Path(workspace) / "validators" / "_ref"
    write(ref, "generate.py", Path(__file__).read_text())
    write(ref, "common.py", (here / "common.py").read_text())
    for name, t in generate(seed)["formats"].items():
        write(Path(workspace) / "validators", f"{name}.py", ORACLE.format(params=t["params"]))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["formats"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": 500}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Partner identifier validation

The partner onboarding form must reject malformed identifiers before they
reach the partner systems. For every format specified in `/workspace/specs/`,
write `validators/<format>.py` exposing `is_valid(text: str) -> bool`, exactly
as the specification defines it. Standard library only.

Each spec gives a few valid examples. Your validators will be tested on
identifiers you have not seen, valid and invalid.
"""

META = {
    "unit": "identifier format", "kind": "validator writing", "domain": "identifier specs", "output_tokens": 1600, "needs_pytest": False,
    "failure_mode": "implementing a precise written specification, graded on unseen near misses",
    "deliverable": "`validators/<format>.py` with `is_valid(text)` for every format",
    "grading": "Per format, all or nothing: every hidden string (valid ones and near misses) classified "
               "correctly. Reward is the mean.",
    "per_unit": "read the spec's structure, alphabet and check algorithm with its parameters, implement it, and "
                "test it on the examples and on near misses you construct",
    "traps": [
        "**Per-format parameters**: weights, what a check value of 10 becomes, pivot years, separators.",
        "**Real dates only**: 30 February and month 13 are invalid; leap years matter.",
        "**Reserved and forbidden letters.**",
        "**Separators only where allowed**; a regex that strips all hyphens accepts near misses.",
        "**Upper case is part of the format.**",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
