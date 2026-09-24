#!/usr/bin/env bash
set -euo pipefail
cd /workspace
cat > jobs/producer.py <<'PYEOF'
"""Job submission."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')


def submit(store, name, priority="normal"):
    if priority not in _ENCODE:
        raise ValueError(f"unknown priority {priority!r}")
    job_id = f"job-{len(store.all()) + 1:04d}"
    record = {"id": job_id, "name": name, "created": store.tick(),
              "state": "pending", _KEY: _ENCODE[priority]}
    store.put(record)
    return job_id
PYEOF
cat > jobs/scheduler.py <<'PYEOF'
"""Picks the next job to run."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')


def next_job(store):
    pending = [r for r in store.all() if r["state"] == "pending"]
    if not pending:
        return None
    job = min(pending, key=lambda r: (-_RANK[_priority(r)], r["created"]))
    return store.update(job["id"], state="running")
PYEOF
cat > jobs/api.py <<'PYEOF'
"""Read-only API views."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

FIELDS = ("id", "name", "state")


def job_view(store, job_id):
    record = store.get(job_id)
    if record is None:
        raise KeyError(job_id)
    view = {field: record[field] for field in FIELDS}
    view["priority"] = _priority(record)
    return view
PYEOF
cat > jobs/cli.py <<'PYEOF'
"""Terminal output."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')


def format_row(record):
    tag = f"[{_priority(record).upper()}]"
    return f"{tag} {record['id']}  {record['state']:<8} {record['name']}"
PYEOF
