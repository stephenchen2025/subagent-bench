# Impact assessment: YAMLISH-2026-07

Security published `ADVISORY.md` this morning. For every service under
`/workspace/services/`, decide whether it is affected, so we know which ones to
patch first.

- `affected`: the service runs a vulnerable version, and untrusted input can
  reach the vulnerable call.
- `not_affected`: it does not.
- `insufficient`: this cannot be determined from the repository.

Write `/workspace/impact/impact.json`:

```json
{"<service>": {"verdict": "affected", "evidence": "<version source and call site>"}}
```

A service left out counts as wrong. Do not modify the services.
