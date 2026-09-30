# Transit candidate vetting

The pipeline flagged every star in `/workspace/stars/`. Vet each candidate by
`docs/VETTING.md` before the follow-up proposal is written.

Write `/workspace/answer/vetting.json`:

```json
{"KOI-NNNN": {"class": "planet", "period_days": 0.0, "radius_earth": 0.0},
 "KOI-MMMM": {"class": "eclipsing_binary"},
 "KOI-LLLL": {"class": "no_signal"}}
```
