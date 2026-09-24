25 production services are degraded: `geo-lookup`, `shipment-tracker`, `webhook-relay`, `loyalty-points`, `price-watch`, `rate-limiter`, `ledger`, `session-store`, `review-moderator`, `catalog-api`, `returns-desk`, `cdn-purger`, `quota-keeper`, `pdf-stamper`, `key-vault`, `feed-builder`, `audit-trail`, `tax-calc`, `fraud-score`, `sms-gateway`, `chat-router`, `inventory-sync`, `notifier`, `cart-merge`, `media-resizer`.

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
