#!/usr/bin/env python3
"""LH22 -- reconcile 50 merchant accounts against the bank, contract by contract.

recon/<merchant>/ holds the internal ledger (ledger.csv), what the bank paid
out (bank.csv), and the merchant's CONTRACT.md. rates.csv holds daily FX
rates. The bank pays each sale NET of fees -- and every contract computes
"net" its own way:

- the fee is `pct` percent plus a fixed amount, with each merchant's numbers;
- foreign-currency sales convert to EUR at the sale date's rate either BEFORE
  or AFTER the fee is taken (the contract says which);
- refunds either carry no fee, or the fee is not given back;
- every amount rounds to cents half-up at the step the contract says;
- settlement is per sale (one bank line per ledger id, ref = the id) or a
  daily batch (one bank line per day, ref BATCH-YYYYMMDD, for the sum).

Per merchant the deliverable lists: ledger ids not settled correctly
(per-sale merchants), bank refs that match nothing, and batch days whose
amount is wrong or missing (batch merchants). Each merchant has planted
anomalies: a missing payout, a payout off by the wrong fee, a duplicated or
unknown bank line, a batch short one sale.

    python3 lh22_reconciliation.py --seed 1 --out /fixture
"""

import datetime as dt
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_MERCHANTS = 50
CURRENCIES = ["EUR", "EUR", "USD", "GBP", "SEK"]
D = Decimal


def cents(x):
    return x.quantize(D("0.01"), rounding=ROUND_HALF_UP)


def rates(seed):
    rng = rng_for(seed, "rates")
    out = {}
    for c, base in (("USD", 0.92), ("GBP", 1.17), ("SEK", 0.087)):
        for day in range(31):
            out[(c, dt.date(2026, 8, 1) + dt.timedelta(days=day))] = D(str(round(base * rng.uniform(0.98, 1.02), 5)))
    return out


def net_eur(tx, c, fx):
    gross = D(tx["gross"])
    rate = D(1) if tx["currency"] == "EUR" else fx[(tx["currency"], tx["date"])]
    refund = gross < 0
    if refund and c["refund_fee"] == "none":
        return cents(gross * rate)
    if c["fx_first"]:
        eur = cents(gross * rate)
        fee = cents(abs(eur) * c["pct"] / 100 + c["fixed"])
        return eur - fee if not refund else eur - fee
    fee = cents(abs(gross) * c["pct"] / 100 + c["fixed"])
    return cents((gross - fee) * rate)


def contract_md(name, c):
    return f"""# Merchant agreement -- {name}

- Fees: {c['pct']}% of each transaction plus EUR {c['fixed']} per transaction.
- Currency: {"sales in other currencies are converted to EUR at the sale date's rate first, and the fee is computed on the EUR amount" if c['fx_first'] else "the fee is computed in the sale currency (the fixed part as the same number of units of that currency) and the net amount is then converted to EUR at the sale date's rate"}.
- Refunds (negative gross): {"returned in full; no fee applies" if c['refund_fee'] == 'none' else "the fee is charged on refunds too and is not given back"}.
- Rounding: every amount is rounded to the cent, half up, as soon as it is computed.
- Settlement: {"one payout per transaction, referenced by the ledger id" if c['mode'] == 'per_sale' else "one payout per calendar day for the sum of that day's net amounts, referenced BATCH-YYYYMMDD"}.
"""


def build(rng, name, fx):
    c = {"pct": D(rng.choice(["1.4", "1.9", "2.5", "2.9", "3.4"])), "fixed": D(rng.choice(["0.10", "0.25", "0.30"])),
         "fx_first": rng.random() < 0.5, "refund_fee": rng.choice(["none", "kept"]),
         "mode": rng.choice(["per_sale", "per_sale", "batch"])}
    ledger = []
    for i in range(rng.randint(25, 45)):
        day = dt.date(2026, 8, 1) + dt.timedelta(days=rng.randint(0, 27))
        gross = D(str(round(rng.uniform(5, 600), 2)))
        if rng.random() < 0.1:
            gross = -gross
        ledger.append({"id": f"{name[:3].upper()}-{i + 1:05d}", "date": day, "gross": str(gross),
                       "currency": rng.choice(CURRENCIES)})
    ledger.sort(key=lambda t: (t["date"], t["id"]))
    bank, truth = [], {"unsettled": [], "unexpected": [], "bad_batches": []}
    if c["mode"] == "per_sale":
        for tx in ledger:
            amount = net_eur(tx, c, fx)
            roll = rng.random()
            if roll < 0.05:
                truth["unsettled"].append(tx["id"])           # never paid out
                continue
            if roll < 0.10:
                amount += D("0.01") * rng.choice([-30, -12, 7, 25])  # paid with the wrong fee
                truth["unsettled"].append(tx["id"])
            bank.append({"date": tx["date"] + dt.timedelta(days=2), "ref": tx["id"], "amount": amount})
            if rng.random() < 0.03:
                bank.append({"date": tx["date"] + dt.timedelta(days=3), "ref": tx["id"] + "-DUP", "amount": amount})
                truth["unexpected"].append(tx["id"] + "-DUP")
    else:
        days = sorted({t["date"] for t in ledger})
        for day in days:
            txs = [t for t in ledger if t["date"] == day]
            total = sum((net_eur(t, c, fx) for t in txs), D(0))
            roll = rng.random()
            if roll < 0.08:
                truth["bad_batches"].append(day.isoformat())   # batch missing entirely
                continue
            if roll < 0.18 and len(txs) > 1:
                total -= net_eur(txs[-1], c, fx)               # one sale left out
                truth["bad_batches"].append(day.isoformat())
            bank.append({"date": day + dt.timedelta(days=1), "ref": f"BATCH-{day:%Y%m%d}", "amount": total})
    if rng.random() < 0.4:
        ref = f"MISC-{rng.randint(1000, 9999)}"
        bank.append({"date": dt.date(2026, 8, rng.randint(2, 29)), "ref": ref, "amount": D(str(round(rng.uniform(10, 90), 2)))})
        truth["unexpected"].append(ref)
    bank.sort(key=lambda b: (b["date"], b["ref"]))
    ledger_csv = "id,date,gross,currency\n" + "".join(f"{t['id']},{t['date']},{t['gross']},{t['currency']}\n" for t in ledger)
    bank_csv = "date,ref,amount_eur\n" + "".join(f"{b['date']},{b['ref']},{b['amount']}\n" for b in bank)
    return c, ledger_csv, bank_csv, {k: sorted(v) for k, v in truth.items()}


def generate(seed, out=None):
    fx = rates(seed)
    rng = rng_for(seed, "plan")
    words = ["alder", "birch", "cedar", "delta", "ember", "fjord", "grove", "harbor", "iris", "juniper", "kestrel",
             "lumen", "maple", "north", "onyx", "pine", "quartz", "river", "sable", "tundra", "umber", "vale"]
    names = rng.sample([f"{a}-{b}" for a in words for b in ("store", "labs", "goods")], N_MERCHANTS)
    files = {"recon/rates.csv": "currency,date,rate_to_eur\n" + "".join(f"{c},{d},{r}\n" for (c, d), r in sorted(fx.items()))}
    truth = {"seed": seed, "merchants": {}}
    for name in names:
        c, ledger_csv, bank_csv, t = build(rng_for(seed, "m", name), name, fx)
        files[f"recon/{name}/ledger.csv"] = ledger_csv
        files[f"recon/{name}/bank.csv"] = bank_csv
        files[f"recon/{name}/CONTRACT.md"] = contract_md(name, c)
        truth["merchants"][name] = {**t, "unit_chars": len(ledger_csv) + len(bank_csv) + 1500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


KEYS = ("unsettled", "unexpected", "bad_batches")


def grade(seed, answer):
    """Per merchant, all or nothing: all three lists exactly right (every
    merchant has at least one anomaly, so empty answers earn nothing)."""
    truth = generate(seed)
    per = {}
    for name, t in truth["merchants"].items():
        got = answer.get(name) if isinstance(answer.get(name), dict) else {}
        per[name] = float(all(sorted(set(map(str, got.get(k) or []))) == t[k] for k in KEYS))
    return {"reward": round(sum(per.values()) / len(per), 4), "merchants": per}


def oracle(seed):
    return {n: {k: t[k] for k in KEYS} for n, t in generate(seed)["merchants"].items()}


def solve(seed, path):
    import json
    write(Path(path).parent, Path(path).name, json.dumps(oracle(seed), indent=2))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [m["unit_chars"] for m in t["merchants"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": 3000}


ANSWER_PATH = "/workspace/answer/recon.json"
INSTRUCTION = """\
# August payout reconciliation

Finance is closing August. For every merchant under `/workspace/recon/`,
reconcile what the bank paid out (`bank.csv`) against what we booked
(`ledger.csv`), under the terms of that merchant's `CONTRACT.md`. FX rates are
in `recon/rates.csv`.

Write `/workspace/answer/recon.json`:

```json
{"<merchant>": {"unsettled": ["<ledger ids paid wrongly or not at all>"],
                "unexpected": ["<bank refs that match no ledger entry>"],
                "bad_batches": ["<YYYY-MM-DD days whose batch is wrong or missing>"]}}
```

Use empty lists where there is nothing to report. A merchant left out counts
as wrong.
"""

META = {
    "unit": "merchant", "kind": "record matching", "domain": "payments ledger", "output_tokens": 1400, "needs_pytest": False,
    "failure_mode": "per-unit contract terms that change the arithmetic",
    "deliverable": "`/workspace/answer/recon.json`",
    "grading": "Per merchant, all or nothing: all three lists exactly right. Reward is the mean.",
    "per_unit": "read the merchant's contract, compute every expected payout (fee, FX order, refund rule, "
                "rounding, settlement mode), and diff against the bank lines",
    "traps": [
        "**FX before or after the fee** gives different cents; so does the fixed fee in sale currency.",
        "**Refund fee rules differ.**",
        "**Batch merchants** settle daily sums; a batch short one sale is a bad batch, not an unsettled id.",
        "**Wrong-fee payouts** are off by cents, not missing.",
    ],
}


def main(argv=None):
    from common import standard_main as sm
    sm(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=True)


if __name__ == "__main__":
    main()
