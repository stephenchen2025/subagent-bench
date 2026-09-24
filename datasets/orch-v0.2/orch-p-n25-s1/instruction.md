25 production services are degraded: `feed-builder`, `pdf-stamper`, `cdn-purger`, `survey-collector`, `job-reaper`, `dns-updater`, `session-store`, `authz`, `cart-merge`, `sms-gateway`, `webhook-relay`, `tax-calc`, `email-digest`, `invoice-render`, `sso-bridge`, `loyalty-points`, `returns-desk`, `key-vault`, `ledger`, `search-indexer`, `catalog-api`, `payout-batch`, `billing-sync`, `export-worker`, `media-resizer`.

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
