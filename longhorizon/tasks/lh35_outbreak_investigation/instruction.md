# Outbreak line lists for the regional health team

Every folder in `/workspace/outbreaks/` is one reported food-borne outbreak:
the event and its attendees' questionnaires. Analyse each by
`docs/CASE_DEFINITION.md`: count the cases, and name the vehicle with its
risk ratio.

Write `/workspace/answer/outbreaks.json`:

```json
{"OB-NN": {"cases": 0, "vehicle": "food as written on the menu", "rr": 0.0}}
```
