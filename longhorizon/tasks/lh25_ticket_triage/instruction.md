# Morning queue triage

Triage every ticket in `/workspace/tickets/` according to
`docs/SUPPORT_POLICY.md`. Customer plans are in `accounts.csv`; the knowledge
base is in `kb/`.

Write `/workspace/answer/triage.json`:

```json
{"T-NNNN": {"category": "...", "priority": "P1", "route": "...", "kb_article": "KB-NNN" or null,
            "duplicate_of": "T-NNNN" or null}}
```
