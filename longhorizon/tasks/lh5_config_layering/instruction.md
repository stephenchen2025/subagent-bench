# Effective production config audit

Before the capacity review we need to know what every service under
`/workspace/services/` actually runs with in **prod**. Read `docs/CONFIG.md`
for how configuration resolves, and `docs/SLO_LIMITS.md` for the limits.

For each service, give the effective prod value of `db.pool_size`,
`http.timeout_s` (seconds), `feature.new_checkout` and `cache.ttl_s`, and list
which of those settings break a limit.

Write `/workspace/answer/effective.json`:

```json
{
  "<service>": {"db.pool_size": 20, "http.timeout_s": 12.5, "feature.new_checkout": true,
                "cache.ttl_s": 300, "violations": ["db.pool_size"]}
}
```

A service left out counts as wrong. Do not change any configuration.
