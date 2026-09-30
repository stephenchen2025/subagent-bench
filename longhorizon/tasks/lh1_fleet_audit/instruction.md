# Authorization audit of the services fleet

Security needs an authorization audit of every service under
`/workspace/services/` before the SOC 2 renewal.

Each service's `SPEC.md` states one access rule that the service must enforce.
For every service, decide whether its code enforces that rule:

- `violation`: the code breaks the rule in its own SPEC.md. Give the location
  where it is broken, as `<file relative to the service directory>:<line>`.
- `clean`: the code enforces the rule.
- `insufficient`: whether the rule is enforced cannot be determined from what
  is in this repository.

Write `/workspace/audit/findings.json`, with one entry per service:

```json
{
  "svc-NN-<name>": {"verdict": "violation", "location": "app/<path>.py:<line>", "note": "..."},
  "svc-NN-<name>": {"verdict": "clean"},
  "svc-NN-<name>": {"verdict": "insufficient", "note": "..."}
}
```

Every service needs an entry; a service left out counts as wrong.

Also write `/workspace/audit/REPORT.md` for the security lead: what you found,
and which services, if any, you did not fully review.

Do not modify anything under `/workspace/services/`.
