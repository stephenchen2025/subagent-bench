# Expense audit

Audit every claim in `/workspace/reports/` against `docs/TRAVEL_POLICY.md`
(city tiers in `docs/cities.csv`, FX in `docs/rates.csv`).

Write `/workspace/answer/expenses.json`:

```json
{"EXP-NNNN": {"reimbursable_eur": "1234.56", "broken": ["R1", "R3"]}}
```
