# Experiment review board

Every experiment under `/workspace/experiments/` wants to ship. Before the
review board meets, check each write-up against its pre-registration and its
data, following `docs/STANDARDS.md` exactly.

Write `/workspace/answer/verdicts.json`:

```json
{"EXP-NNNN": {"verdict": "supported" | "not_significant" | "srm" | "underpowered" | "wrong_metric"}}
```
