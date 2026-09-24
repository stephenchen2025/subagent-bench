10 production services are degraded: `notifier`, `quota-keeper`, `fraud-score`, `search-indexer`, `geo-lookup`, `rate-limiter`, `billing-sync`, `session-store`, `export-worker`, `ledger`.

For each service, find the component that is failing and the root cause. Use the
`svcctl` tool:

- `svcctl status <service>`: health and incident notes
- `svcctl components <service>`: the service's components
- `svcctl logs <service> <component>`: recent logs for one component

The root cause is exactly one of: `expired-credential`, `disk-full`, `dns-failure`, `config-typo`, `out-of-memory`.

Write the result to `answer.json` in the working directory:

```json
{"services": {"<service>": {"component": "<component>", "cause": "<cause>"}}}
```

Each service is scored separately: half for the component, half for the cause.
