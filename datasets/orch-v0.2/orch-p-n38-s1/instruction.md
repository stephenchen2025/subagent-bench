38 production services are degraded: `survey-collector`, `schema-registry`, `billing-sync`, `catalog-api`, `loyalty-points`, `inventory-sync`, `payout-batch`, `quota-keeper`, `consent-log`, `search-indexer`, `cost-reporter`, `notifier`, `tax-calc`, `returns-desk`, `review-moderator`, `media-resizer`, `chat-router`, `label-printer`, `session-store`, `audit-trail`, `export-worker`, `shipment-tracker`, `dns-updater`, `sms-gateway`, `sso-bridge`, `ledger`, `fraud-score`, `thumbnailer`, `email-digest`, `ledger-archiver`, `price-watch`, `cdn-purger`, `authz`, `invoice-render`, `rate-limiter`, `pdf-stamper`, `geo-lookup`, `feed-builder`.

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
