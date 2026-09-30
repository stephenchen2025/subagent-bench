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
