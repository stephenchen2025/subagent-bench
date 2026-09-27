# Replicate assay results for the lab report

The same sample was assayed on many days; each run is in `/workspace/runs/`
(the plate readings and the operator's notes). Analyse every run by
`docs/PROTOCOL.md`, decide which runs are valid, and summarise the valid ones.

Write `/workspace/answer/replicates.json`:

```json
{"replicates": {"R-NN": {"valid": true, "conc_mg_l": 0.0},
                "R-MM": {"valid": false, "reason": "..."}},
 "summary": {"n_valid": 0, "mean_mg_l": 0.0, "sd_mg_l": 0.0}}
```

Concentrations are for the original, undiluted sample, in mg/L.
