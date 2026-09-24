38 production services are degraded: `sms-gateway`, `returns-desk`, `review-moderator`, `catalog-api`, `sso-bridge`, `chat-router`, `webhook-relay`, `email-digest`, `consent-log`, `thumbnailer`, `schema-registry`, `authz`, `session-store`, `key-vault`, `survey-collector`, `feed-builder`, `audit-trail`, `quota-keeper`, `cost-reporter`, `cart-merge`, `billing-sync`, `price-watch`, `notifier`, `media-resizer`, `geo-lookup`, `fraud-score`, `export-worker`, `backup-rotator`, `dns-updater`, `invoice-render`, `cdn-purger`, `loyalty-points`, `pdf-stamper`, `shipment-tracker`, `payout-batch`, `job-reaper`, `search-indexer`, `tax-calc`.

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
