Add job priorities to the job system in `jobs/`.

Required behaviour:

- `producer.submit(store, name, priority="normal")` accepts `"low"`, `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls without `priority` keep working.
- `scheduler.next_job(store)` returns the highest-priority pending job; ties go to the oldest.
- `api.job_view(store, job_id)` includes `"priority"`, with the value given at submission (e.g. `"high"`).
- `cli.format_row(record)` starts with the priority in capitals in brackets, e.g. `[HIGH] job-0001  pending  build`.
- `exporter.export_csv(store)` has a `priority` column holding `low`/`normal`/`high`.
- `metrics.counts_by_priority(store)` returns `{"low": n, "normal": n, "high": n}`, all three keys always present.
- `archive.unpack(archive.pack(record))` preserves the job's priority.

Jobs submitted before this change have no priority. Treat them as `normal` everywhere.

Files that need changes: `jobs/metrics.py`, `jobs/cli.py`, `jobs/scheduler.py`, `jobs/exporter.py`, `jobs/producer.py`, `jobs/archive.py`, `jobs/api.py`. `python -m unittest discover tests` must keep passing.
