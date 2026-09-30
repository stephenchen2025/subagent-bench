# Systematic review: exercise for depression

The search produced the trial reports in `/workspace/reports/`. Screen and
extract every report by `docs/REVIEW_PROTOCOL.md`, then pool the included
trials.

Write `/workspace/answer/review.json`:

```json
{"studies": {"S-NN": {"include": true, "log_rr": 0.0, "se": 0.0},
             "S-MM": {"include": false, "reason": "..."}},
 "pooled": {"k": 0, "rr": 0.0, "ci_low": 0.0, "ci_high": 0.0}}
```
