38 production services are degraded: `fraud-score`, `sms-gateway`, `consent-log`, `tax-calc`, `survey-collector`, `ledger`, `authz`, `loyalty-points`, `schema-registry`, `sso-bridge`, `quota-keeper`, `price-watch`, `cdn-purger`, `rate-limiter`, `payout-batch`, `email-digest`, `cost-reporter`, `chat-router`, `dns-updater`, `export-worker`, `cart-merge`, `ledger-archiver`, `inventory-sync`, `job-reaper`, `audit-trail`, `search-indexer`, `key-vault`, `label-printer`, `feed-builder`, `invoice-render`, `review-moderator`, `returns-desk`, `geo-lookup`, `catalog-api`, `shipment-tracker`, `thumbnailer`, `webhook-relay`, `media-resizer`.

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
