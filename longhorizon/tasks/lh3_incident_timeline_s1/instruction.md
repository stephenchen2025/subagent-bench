# INC-2317: build the timeline

From the on-call ticket:

> db-primary crashed at about 02:14 UTC and took checkout down with it. Confirm
> that db-primary was the first failure, and build the incident timeline for the
> postmortem.

Everything we have is in `/workspace/incident/`, with one directory per host.
Start with `incident/README.md`.

Write `/workspace/answer/timeline.json`:

```json
{
  "premise_correct": false,
  "root_cause": {"host": "...", "kind": "..."},
  "events": [
    {"host": "...", "kind": "...", "utc": "2026-09-14T02:09:12Z"}
  ]
}
```

- `premise_correct`: was db-primary really the first failure?
- `events`: the incident's causal chain, in order. Give one entry per kind, at
  that kind's first occurrence anywhere in the fleet, with the timestamp in
  true UTC (corrected for that host's clock). List only events that are part of
  this incident.
- `kind` must be one of: `cert_reload`, `tls_handshake_failure`, `retry_storm`, `queue_backlog`, `worker_oom`, `cache_eviction_storm`, `cache_miss_fallback`, `db_connection_saturation`, `db_failover`, `replica_promoted`, `db_autovacuum_warning`, `cron_job_failure`, `signing_key_rotation`, `deploy`, `config_change`.
