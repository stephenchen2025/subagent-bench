#!/usr/bin/env python3
"""LH24 -- extract the commercial terms of 56 vendor contracts, amendments included.

contracts/<vendor>/CONTRACT.md is a vendor agreement in prose, some with
AMENDMENT-1.md and AMENDMENT-2.md that change it (later documents win).
docs/FIELDS.md defines seven fields to extract, as of 2026-09-26.

Nothing is in one place or one format:

- numbers are written as words with digits in brackets ("thirty (30) days")
  or as words alone; dates as "1 March 2025", "01.03.2025" or "March 1, 2025";
- notice may be given in months (a month counts as 30 days);
- the renewal term may differ from the initial term, and the next renewal date
  depends on which applies;
- the liability cap is either a fixed amount or "the fees paid in the preceding
  twelve months" -- twelve times the monthly fee, converted at the contract's
  own fixed rate if the fee is in USD;
- an amendment can extend the term, drop auto-renewal, change the notice
  period or the governing law.

    python3 lh24_contract_terms.py --seed 1 --out /fixture
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_CONTRACTS = 56
AS_OF = dt.date(2026, 9, 26)
FIELDS = ["start_date", "term_months", "auto_renew", "notice_days", "next_renewal", "liability_cap_eur",
          "governing_law"]
NUM_WORDS = {3: "three", 6: "six", 12: "twelve", 18: "eighteen", 24: "twenty-four", 30: "thirty",
             36: "thirty-six", 45: "forty-five", 60: "sixty", 90: "ninety", 1: "one", 2: "two"}
LAWS = ["Germany", "the Netherlands", "Ireland", "France", "England and Wales", "Sweden"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


LEGAL = [
    "Headings are for convenience only and do not affect interpretation.",
    "Each party shall comply with all laws applicable to its performance of this agreement.",
    "Neither party may assign this agreement without the other party's prior written consent, not to be unreasonably withheld.",
    "Notices must be in writing and delivered by hand, courier or email to the addresses set out in Schedule 1.",
    "Supplier shall maintain insurance appropriate to the Services with a reputable insurer.",
    "Any variation of this agreement must be in writing and signed by both parties.",
    "Confidential Information excludes information that is or becomes public other than through a breach of this clause.",
    "The receiving party shall use Confidential Information only to perform its obligations under this agreement.",
    "Supplier warrants that the Services will be performed with reasonable skill and care.",
    "If any provision is held invalid, the remainder of this agreement continues in full force.",
    "A failure to exercise a right is not a waiver of that right.",
    "This agreement constitutes the entire agreement between the parties relating to its subject matter.",
]


def legal_prose(rng, n):
    return "\n\n".join(" ".join(rng.sample(LEGAL, rng.randint(3, 5))) for _ in range(n))


def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    return d.replace(year=d.year + y, month=m + 1)


def words(n, rng, style=None):
    style = style or rng.choice(["both", "both", "words", "digits"])
    if style == "digits" or n not in NUM_WORDS:
        return str(n)
    return f"{NUM_WORDS[n]} ({n})" if style == "both" else NUM_WORDS[n]


def date_text(d, rng):
    return rng.choice([f"{d.day} {MONTHS[d.month - 1]} {d.year}", f"{d.day:02d}.{d.month:02d}.{d.year}",
                       f"{MONTHS[d.month - 1]} {d.day}, {d.year}"])


def terms(rng):
    start = dt.date(rng.choice([2023, 2024, 2025]), rng.randint(1, 12), 1)
    t = {"start_date": start, "term_months": rng.choice([12, 24, 36]), "auto_renew": rng.random() < 0.7,
         "renewal_months": None, "notice_value": rng.choice([30, 60, 90]), "notice_unit": "days",
         "law": rng.choice(LAWS), "cap_kind": rng.choice(["fixed", "fees"]),
         "cap_fixed": rng.choice([100000, 250000, 500000, 1000000]), "fee": rng.choice([2500, 4000, 7500, 12000]),
         "fee_ccy": rng.choice(["EUR", "EUR", "USD"]), "usd_rate": rng.choice(["0.92", "0.90", "0.95"])}
    if t["auto_renew"] and rng.random() < 0.5:
        t["renewal_months"] = rng.choice([6, 12])
    if rng.random() < 0.3:
        t["notice_value"], t["notice_unit"] = rng.choice([1, 2, 3]), "months"
    return t


def resolve(t):
    notice = t["notice_value"] * (30 if t["notice_unit"] == "months" else 1)
    end = add_months(t["start_date"], t["term_months"])
    if t["auto_renew"]:
        step = t["renewal_months"] or t["term_months"]
        nxt = end
        while nxt < AS_OF:
            nxt = add_months(nxt, step)
    else:
        nxt = end
    fee_eur = t["fee"] * (float(t["usd_rate"]) if t["fee_ccy"] == "USD" else 1)
    cap = round(12 * fee_eur, 2) if t["cap_kind"] == "fees" else float(t["cap_fixed"])
    return {"start_date": t["start_date"].isoformat(), "term_months": t["term_months"], "auto_renew": t["auto_renew"],
            "notice_days": notice, "next_renewal": nxt.isoformat(), "liability_cap_eur": cap,
            "governing_law": t["law"]}


def contract_text(vendor, t, rng):
    parts = [f"# Master Services Agreement -- {vendor}", "",
             f"This agreement is made between Acme Shop B.V. (\"Customer\") and {vendor} (\"Supplier\").", "",
             "## 1. Definitions", "", legal_prose(rng, 2), "",
             "## 2. Services", "", legal_prose(rng, 2), "",
             "## 3. Fees", "",
             f"Customer shall pay a monthly fee of {t['fee_ccy']} {t['fee']:,}." + (
                 f" For all purposes under this agreement, USD amounts convert to EUR at a fixed rate of "
                 f"{t['usd_rate']} EUR per USD." if t["fee_ccy"] == "USD" else ""), "",
             "## 4. Term and renewal", "",
             f"4.1 This agreement commences on {date_text(t['start_date'], rng)} (the \"Effective Date\").",
             f"4.2 The Initial Term is {words(t['term_months'], rng)} months from the Effective Date."]
    if t["auto_renew"]:
        rt = t["renewal_months"]
        parts.append("4.3 Thereafter this agreement renews automatically for successive periods of "
                     + (f"{words(rt, rng)} months" if rt else "the same length as the Initial Term")
                     + " unless terminated in accordance with clause 4.4.")
    else:
        parts.append("4.3 This agreement expires at the end of the Initial Term and does not renew.")
    unit = t["notice_unit"]
    parts += [f"4.4 Either party may prevent renewal by giving {words(t['notice_value'], rng)} "
              f"{unit if t['notice_value'] != 1 else unit[:-1]}' written notice before the end of the then-current term.",
              "", "## 5. Liability", "",
              (f"5.1 Each party's aggregate liability is capped at EUR {t['cap_fixed']:,}." if t["cap_kind"] == "fixed"
               else "5.1 Each party's aggregate liability is capped at the total fees paid by Customer in the "
                    "twelve (12) months preceding the claim, which for the purposes of this agreement equals "
                    "twelve times the monthly fee."),
              "", "## 6. Confidentiality", "", legal_prose(rng, 3), "",
              "## 7. Governing law", "", f"This agreement is governed by the laws of {t['law']}.", ""]
    return "\n".join(parts)


def amendments(t, rng):
    """Zero to two amendments; each mutates `t` and returns its text."""
    texts = []
    for n in range(rng.choice([0, 0, 1, 1, 2])):
        kind = rng.choice(["term", "renew_off", "notice", "law", "cap"])
        if kind == "term":
            t["term_months"] = rng.choice([x for x in (18, 30, 36, 48) if x != t["term_months"]])
            text = f"Clause 4.2 is replaced: \"The Initial Term is {words(t['term_months'], rng)} months from the Effective Date.\""
        elif kind == "renew_off" and t["auto_renew"]:
            t["auto_renew"] = False
            text = "Clause 4.3 is replaced: \"This agreement expires at the end of the Initial Term and does not renew.\""
        elif kind == "notice":
            t["notice_value"], t["notice_unit"] = rng.choice([(45, "days"), (60, "days"), (2, "months")])
            text = (f"Clause 4.4 is amended so that the notice period is {words(t['notice_value'], rng)} "
                    f"{t['notice_unit']}.")
        elif kind == "law":
            t["law"] = rng.choice([x for x in LAWS if x != t["law"]])
            text = f"Clause 7 is amended: this agreement is governed by the laws of {t['law']}."
        else:
            t["cap_kind"], t["cap_fixed"] = "fixed", rng.choice([150000, 750000])
            text = f"Clause 5.1 is replaced: \"Each party's aggregate liability is capped at EUR {t['cap_fixed']:,}.\""
        texts.append(f"# Amendment {n + 1}\n\nWith effect from {date_text(add_months(t['start_date'], 6 * (n + 1)), rng)}, "
                     f"the parties agree:\n\n{text}\n\nAll other terms remain unchanged.\n")
    return texts


FIELDS_MD = f"""# Contract fields (as of {AS_OF.isoformat()})

Later amendments override earlier ones, and both override the base agreement.

- `start_date`: the Effective Date, ISO `YYYY-MM-DD`.
- `term_months`: the Initial Term in months, after amendments.
- `auto_renew`: true if the agreement renews automatically.
- `notice_days`: the notice period in days; a month counts as 30 days.
- `next_renewal`: for renewing agreements, the first end-of-term date on or
  after {AS_OF.isoformat()} (the Initial Term, then successive renewal periods);
  for non-renewing ones, the end of the Initial Term (even if in the past).
- `liability_cap_eur`: the cap in EUR as a number; if defined by fees, twelve
  times the monthly fee converted at the contract's own rate.
- `governing_law`: the jurisdiction exactly as the contract names it.
"""


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    names = ["Northwind", "Contoso", "Fabrikam", "Globex", "Initech", "Umbrella", "Hooli", "Vandelay", "Stark",
             "Wayne", "Tyrell", "Cyberdyne", "Soylent", "Wonka", "Acme Cloud", "Oscorp"]
    vendors = rng.sample([f"{n} {k}" for n in names for k in ("GmbH", "B.V.", "Ltd", "AB")], N_CONTRACTS)
    files = {"docs/FIELDS.md": FIELDS_MD}
    truth = {"seed": seed, "contracts": {}}
    for vendor in vendors:
        crng = rng_for(seed, "c", vendor)
        slug = vendor.lower().replace(" ", "-").replace(".", "")
        t = terms(crng)
        files[f"contracts/{slug}/CONTRACT.md"] = contract_text(vendor, t, crng)
        for i, text in enumerate(amendments(t, crng), 1):
            files[f"contracts/{slug}/AMENDMENT-{i}.md"] = text
        truth["contracts"][slug] = {**resolve(t), "unit_chars": len(files[f"contracts/{slug}/CONTRACT.md"]) + 1500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def _eq(a, b):
    if isinstance(b, bool):
        return a is b
    if isinstance(b, (int, float)) and not isinstance(a, bool):
        try:
            return abs(float(a) - float(b)) < 0.005
        except (TypeError, ValueError):
            return False
    return isinstance(a, str) and a.strip() == b


def grade(seed, answer):
    """Per contract: the fraction of the seven fields exactly right. Reward is the mean."""
    truth = generate(seed)
    per = {}
    for slug, t in truth["contracts"].items():
        got = answer.get(slug) if isinstance(answer.get(slug), dict) else {}
        per[slug] = round(sum(_eq(got.get(f), t[f]) for f in FIELDS) / len(FIELDS), 4)
    return {"reward": round(sum(per.values()) / len(per), 4), "contracts": per}


def oracle(seed):
    return {s: {f: t[f] for f in FIELDS} for s, t in generate(seed)["contracts"].items()}


def solve(seed, path):
    import json
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [c["unit_chars"] for c in t["contracts"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(FIELDS_MD)}


ANSWER_PATH = "/workspace/answer/contracts.json"
INSTRUCTION = """\
# Vendor contract register

Procurement is building a register of our vendor agreements. For every vendor
under `/workspace/contracts/`, extract the fields defined in `docs/FIELDS.md`
from its agreement and any amendments.

Write `/workspace/answer/contracts.json`, keyed by the vendor's directory name:

```json
{"<vendor-dir>": {"start_date": "YYYY-MM-DD", "term_months": 24, "auto_renew": true, "notice_days": 90,
                  "next_renewal": "YYYY-MM-DD", "liability_cap_eur": 250000, "governing_law": "..."}}
```
"""

META = {
    "unit": "contract", "kind": "term extraction", "domain": "legal contracts", "output_tokens": 1300, "needs_pytest": False,
    "failure_mode": "reading legal prose precisely, where amendments override and values need computing",
    "deliverable": "`/workspace/answer/contracts.json`",
    "grading": "Per contract: the fraction of seven fields exactly right. Reward is the mean.",
    "per_unit": "read the agreement and its amendments in order, normalise words and dates, and compute "
                "notice days, the next renewal date and the liability cap",
    "traps": [
        "**Amendments override**, and a later one can override an earlier one.",
        "**Numbers as words** and three date formats.",
        "**Notice in months** is 30 days each.",
        "**Renewal periods can differ** from the initial term.",
        "**Fee-based caps** are twelve monthly fees at the contract's own USD rate.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
