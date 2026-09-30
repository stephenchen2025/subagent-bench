# When does each job run next?

Operations is migrating every job in `/workspace/jobs/` to a new scheduler that
only understands UTC timestamps. For each job, work out its next three run
times strictly after 2026-09-26T00:00:00Z, using the calendar of the job's
region in `docs/regions/`.

Write `/workspace/answer/runs.json`:

```json
{"<job>": ["2026-09-28T06:30:00Z", "...", "..."]}
```
