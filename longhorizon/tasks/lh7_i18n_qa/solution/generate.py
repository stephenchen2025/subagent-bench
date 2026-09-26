#!/usr/bin/env python3
"""LH7 -- QA 48 translation files against the source strings before release.

locales/en.json is the source catalogue (about 200 messages); locales/<lang>.json
are 48 translations delivered by vendors. docs/L10N_RULES.md defines six
errors, and every one needs a per-language or per-key fact:

- E1 placeholder mismatch -- the translation must use exactly the source's
  `{placeholders}`, including inside plural branches;
- E2 missing plural category -- ICU plural messages need every category the
  target language requires (Polish needs one/few/many/other; Japanese only
  other; Arabic six), from the table in the rules;
- E3 too long -- keys with a UI limit (ui_limits.json) may not exceed it,
  counted in characters, not bytes;
- E4 untranslated -- identical to the English source, unless the key is on the
  do-not-translate list (brand names);
- E5 missing key, E6 key not in the source.

The deliverable lists every error in every file. Each language is its own
review against its own plural rules.

    python3 lh7_i18n_qa.py --seed 1 --out /fixture
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_LOCALES = 48
PLURALS = {"pl": ["one", "few", "many", "other"], "ru": ["one", "few", "many", "other"], "uk": ["one", "few", "many", "other"],
           "cs": ["one", "few", "many", "other"], "ar": ["zero", "one", "two", "few", "many", "other"],
           "ja": ["other"], "zh": ["other"], "ko": ["other"], "fr": ["one", "many", "other"], "de": ["one", "other"],
           "nl": ["one", "other"], "sv": ["one", "other"], "es": ["one", "many", "other"], "it": ["one", "many", "other"],
           "pt": ["one", "many", "other"], "ga": ["one", "two", "few", "many", "other"], "cy": ["zero", "one", "two", "few", "many", "other"],
           "lt": ["one", "few", "many", "other"], "ro": ["one", "few", "other"], "sl": ["one", "two", "few", "other"]}
WORDS = ["order", "invoice", "cart", "account", "payment", "delivery", "review", "coupon", "address", "profile",
         "report", "message", "item", "team", "project"]
BRANDS = ["brand.name", "brand.tagline_product", "legal.company"]


def source_catalogue(rng):
    cat, limits = {}, {}
    for i in range(200):
        w = rng.choice(WORDS)
        kind = rng.random()
        key = f"{rng.choice(['checkout', 'settings', 'orders', 'account', 'nav', 'errors'])}.{w}_{i:03d}"
        if kind < 0.3:
            cat[key] = f"Your {w} {{name}} was updated on {{date}}."
        elif kind < 0.45:
            cat[key + ".plural"] = f"{{count, plural, one {{# {w}}} other {{# {w}s}}}}"
        else:
            cat[key] = f"{w.capitalize()} {rng.choice(['saved', 'removed', 'not found', 'pending', 'shared'])}"
        if kind > 0.6 and rng.random() < 0.5:
            limits[key] = rng.choice([16, 20, 24])
    for b in BRANDS:
        cat[b] = {"brand.name": "Acme Shop", "brand.tagline_product": "Acme Checkout", "legal.company": "Acme Shop B.V."}[b]
    return cat, limits


def translate(src, lang, key):
    """A stand-in 'translation': deterministic and visibly different from English."""
    if key in BRANDS:
        return src
    if key.endswith(".plural"):
        cats = PLURALS[lang]
        noun = re.search(r"one \{# (\w+)\}", src).group(1)
        return "{count, plural, " + " ".join(f"{c} {{# {noun}-{lang}-{c}}}" for c in cats) + "}"
    out = src
    for a, b in (("Your", f"[{lang}] Ihr"), ("was updated on", "aktualisiert am"), ("saved", "ok"), ("removed", "weg"),
                 ("not found", "fehlt"), ("pending", "offen"), ("shared", "geteilt")):
        out = out.replace(a, b)
    if out == src:
        out = f"[{lang}] {src}"
    return out


def build_locale(rng, lang, cat, limits):
    tr = {k: translate(v, lang, k) for k, v in cat.items()}
    errors = set()
    keys = [k for k in cat if k not in BRANDS]
    for _ in range(rng.randint(2, 6)):
        k = rng.choice(keys)
        kind = rng.choice(["E1", "E2", "E3", "E4", "E5", "E6"])
        if kind == "E1" and "{name}" in cat[k]:
            tr[k] = tr[k].replace("{name}", "{nom}")
            errors.add(f"{k}:E1")
        elif kind == "E1" and k.endswith(".plural"):
            tr[k] = tr[k].replace("{# ", "{", 1)  # drops the # placeholder in one branch
            errors.add(f"{k}:E1")
        elif kind == "E2" and k.endswith(".plural") and len(PLURALS[lang]) > 1:
            drop = rng.choice(PLURALS[lang][:-1])
            tr[k] = re.sub(rf"{drop} \{{[^}}]*\}} ", "", tr[k])
            errors.add(f"{k}:E2")
        elif kind == "E3" and k in limits:
            tr[k] = tr[k] + " " + "ÿ" * (limits[k])  # multi-byte, so a byte count overstates it
            errors.add(f"{k}:E3")
        elif kind == "E4" and not k.endswith(".plural"):
            tr[k] = cat[k]
            errors.add(f"{k}:E4")
        elif kind == "E5":
            tr.pop(k, None)
            errors = {e for e in errors if not e.startswith(k + ":")}
            errors.add(f"{k}:E5")
        elif kind == "E6":
            extra = f"legacy.{rng.choice(WORDS)}_{rng.randint(100, 999)}"
            tr[extra] = "Alt"
            errors.add(f"{extra}:E6")
    # A near miss that is NOT an error: a string at exactly its limit, counted in characters.
    fit = [k for k in keys if k in limits and not k.endswith(".plural") and f"{k}:E3" not in errors and k in tr]
    if fit:
        k = rng.choice(fit)
        tr[k] = ("é" * limits[k])
    return tr, sorted(errors)


def check(src, tr, lang, limits, dnt):
    """The rules, as docs/L10N_RULES.md states them."""
    errs = set()
    ph = lambda s: set(re.findall(r"\{(\w+)\}", s)) | ({"#"} if "#" in s else set())  # noqa: E731
    for k, v in src.items():
        if k not in tr:
            errs.add(f"{k}:E5")
            continue
        t = tr[k]
        if k.endswith(".plural"):
            branches = dict(re.findall(r"(\w+) \{([^}]*)\}", t.split("plural,", 1)[1]))
            if any(set(re.findall(r"\{(\w+)\}", b)) or "#" not in b for b in branches.values()):
                errs.add(f"{k}:E1")
            if set(PLURALS[lang]) - set(branches):
                errs.add(f"{k}:E2")
        elif ph(v) != ph(t):
            errs.add(f"{k}:E1")
        if k in limits and len(t) > limits[k]:
            errs.add(f"{k}:E3")
        if t == v and k not in dnt and not k.endswith(".plural"):
            errs.add(f"{k}:E4")
    for k in tr:
        if k not in src:
            errs.add(f"{k}:E6")
    return sorted(errs)


RULES = """# Localisation QA rules

Check every `locales/<lang>.json` against `locales/en.json`. Report each error
as `<key>:<code>`.

- **E1** Placeholders: a translation must contain exactly the placeholders
  (`{name}`) of its source. In ICU plural messages
  (`{count, plural, one {...} other {...}}`), every branch must contain `#`
  and no other placeholder.
- **E2** Plural categories: a plural message must have a branch for every
  category its language requires:

""" + "\n".join(f"  - `{lang}`: {', '.join(c)}" for lang, c in PLURALS.items()) + """

- **E3** Length: keys in `ui_limits.json` may not exceed their limit, counted
  in characters (not bytes).
- **E4** Untranslated: a non-plural translation identical to its English
  source, unless the key is in `do_not_translate.json`.
- **E5** A source key missing from the translation (report nothing else for it).
- **E6** A key in the translation that is not in the source.
"""


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    cat, limits = source_catalogue(rng)
    langs = list(PLURALS)
    locales = [f"{lang}" if i < len(langs) else f"{lang}-{region}"
               for i, (lang, region) in enumerate((l, r) for r in ("", "x", "y") for l in langs)][:N_LOCALES]
    locales = [loc.rstrip("-") for loc in locales]
    files = {"docs/L10N_RULES.md": RULES, "locales/en.json": json.dumps(cat, indent=2, ensure_ascii=False) + "\n",
             "locales/ui_limits.json": json.dumps(limits, indent=2) + "\n",
             "locales/do_not_translate.json": json.dumps(BRANDS, indent=2) + "\n"}
    truth = {"seed": seed, "locales": {}}
    for loc in locales:
        lang = loc.split("-")[0]
        tr, planted = build_locale(rng_for(seed, "loc", loc), lang, cat, limits)
        files[f"locales/{loc}.json"] = json.dumps(tr, indent=2, ensure_ascii=False) + "\n"
        errs = check(cat, tr, lang, limits, BRANDS)
        truth["locales"][loc] = {"errors": errs, "unit_chars": len(files[f"locales/{loc}.json"]) + 2000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def grade(seed, answer):
    """Per locale, all or nothing: the exact set of errors."""
    truth = generate(seed)
    per = {}
    for loc, t in truth["locales"].items():
        got = answer.get(loc)
        per[loc] = float(isinstance(got, list) and sorted(set(map(str, got))) == t["errors"])
    return {"reward": round(sum(per.values()) / len(per), 4), "locales": per}


def oracle(seed):
    return {loc: t["errors"] for loc, t in generate(seed)["locales"].items()}


def solve(seed, path):
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [x["unit_chars"] for x in t["locales"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(RULES) + 12000}


ANSWER_PATH = "/workspace/answer/l10n_errors.json"
INSTRUCTION = """\
# Localisation QA before the release

The translation vendors delivered every catalogue in `/workspace/locales/`.
Before we ship, check each one against the English source (`locales/en.json`)
by the rules in `docs/L10N_RULES.md`.

Write `/workspace/answer/l10n_errors.json`, one entry per catalogue:

```json
{"<locale>": ["<key>:<code>", ...]}
```

Use an empty list for a catalogue with no errors.
"""

META = {
    "unit": "locale", "output_tokens": 1400, "needs_pytest": False, "kind": "error list", "domain": "localisation",
    "failure_mode": "per-language rules applied across a whole catalogue",
    "deliverable": "`/workspace/answer/l10n_errors.json`",
    "grading": "Per locale, all or nothing: the exact set of errors. Reward is the mean.",
    "per_unit": "diff the catalogue against the source key by key: placeholders (including plural branches), "
                "the language's plural categories, character-counted limits, untranslated strings, missing and extra keys",
    "traps": [
        "**Plural categories differ by language** (Polish four, Japanese one, Arabic six).",
        "**Placeholders inside plural branches.**",
        "**Characters, not bytes**: a string exactly at its limit in accented letters is fine.",
        "**Brand names** are legitimately identical to English.",
        "**A missing key** is only E5, not also E1-E4.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
