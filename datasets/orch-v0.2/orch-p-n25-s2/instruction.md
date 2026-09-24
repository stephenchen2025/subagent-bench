25 production services are degraded: `sso-bridge`, `feed-builder`, `dns-updater`, `cost-reporter`, `thumbnailer`, `key-vault`, `export-worker`, `backup-rotator`, `sms-gateway`, `survey-collector`, `audit-trail`, `inventory-sync`, `session-store`, `notifier`, `consent-log`, `rate-limiter`, `ledger`, `job-reaper`, `email-digest`, `fraud-score`, `returns-desk`, `geo-lookup`, `promo-engine`, `tax-calc`, `pdf-stamper`.

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
