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
cat > jobs/exporter.py <<'PYEOF'
"""CSV export."""
import csv
import io

_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

COLUMNS = ["id", "name", "state", "priority"]


def export_csv(store):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(COLUMNS)
    for record in store.all():
        writer.writerow([record["id"], record["name"], record["state"],
                         _priority(record)])
    return out.getvalue()
PYEOF
cat > jobs/metrics.py <<'PYEOF'
"""Counters for the dashboard."""
from collections import Counter

_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')


def counts_by_state(store):
    return dict(Counter(r["state"] for r in store.all()))


def counts_by_priority(store):
    counts = {"low": 0, "normal": 0, "high": 0}
    for record in store.all():
        counts[_priority(record)] += 1
    return counts
PYEOF
cat > jobs/archive.py <<'PYEOF'
"""Compact one-line archive format."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')


def pack(record):
    return "|".join([record["id"], record["name"], record["state"],
                     str(record["created"]), _priority(record)])


def unpack(line):
    job_id, name, state, created, priority = line.split("|")
    return {"id": job_id, "name": name, "state": state,
            "created": int(created), _KEY: _ENCODE[priority]}
PYEOF
