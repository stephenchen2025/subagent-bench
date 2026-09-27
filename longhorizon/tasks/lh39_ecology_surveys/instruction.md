# Diversity table for the ground-beetle survey

The season's pitfall-trap results are in `/workspace/plots/`: one folder per
plot with the tally and the observer's field notes. Turn every plot into its
row of the diversity table, following `docs/SURVEY_PROTOCOL.md` and the
checklist in `species.csv`.

Write `/workspace/answer/diversity.json`:

```json
{"PL-NN": {"valid": true, "richness": 0, "shannon": 0.0, "simpson": 0.0, "density_per_100m2": 0.0},
 "PL-MM": {"valid": false}}
```
