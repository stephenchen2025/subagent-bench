"""C -- coupled change. Looks parallel; isn't.

Add a `priority` field to a small job system. The instruction names every file
that must change and specifies the behaviour at the edges: how `submit` is
called, what `next_job` returns, what the API and CLI show. It says nothing about
how priority is stored in the job record. Every module reads and writes the same
records, so that representation is a decision the modules must share.

One agent makes that decision once, without noticing it made it. Isolated workers
each make it separately: one stores `"priority": "high"`, another sorts on
`record.get("prio", 1)`. Each module is locally reasonable; the hidden
integration test fails. This is Cognition's Flappy Bird failure, and the 37% of
MAST failures that are inter-agent misalignment, in a form a verifier can check.

Delegation is not forbidden. A lead that fixes the representation first and
puts it in every brief passes. The label is `solo` because the cheapest correct
policy is not to delegate at all.
"""

import json

from orch.task import SOLO, OrchTask, rng_for, task_id

FAMILY = "C"
SIZES = (4, 7)

CORE = ("producer", "scheduler", "api", "cli")
EXTRA = ("exporter", "metrics", "archive")

LEVELS = ("low", "normal", "high")
# Representations a worker might pick. Each is internally consistent; mixing
# them is what breaks. (key, encoding)
REPRESENTATIONS = [
    ("priority", "str"),
    ("priority", "rank"),
    ("prio", "str"),
    ("prio", "rank"),
    ("level", "rank_inv"),
]
ENCODINGS = {
    "str": {"low": "low", "normal": "normal", "high": "high"},
    "rank": {"low": 0, "normal": 1, "high": 2},
    "rank_inv": {"low": 2, "normal": 1, "high": 0},
}

STORE = '''"""Append-only JSON-lines job store.

Every module in this package reads and writes job records through this store.
"""
import json
import os


class Store:
    def __init__(self, path):
        self.path = path
        self._clock = 0
        if os.path.exists(path):
            for record in self._records():
                self._clock = max(self._clock, record.get("created", 0))

    def _records(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def tick(self):
        self._clock += 1
        return self._clock

    def put(self, record):
        with open(self.path, "a") as fh:
            fh.write(json.dumps(record) + "\\n")

    def all(self):
        latest = {}
        for record in self._records():
            latest[record["id"]] = record
        return list(latest.values())

    def get(self, job_id):
        for record in self.all():
            if record["id"] == job_id:
                return record
        return None

    def update(self, job_id, **fields):
        record = dict(self.get(job_id))
        record.update(fields)
        self.put(record)
        return record
'''

# --- baseline modules (before the feature) -------------------------------------

BASE = {
    "producer": '''"""Job submission."""


def submit(store, name):
    job_id = f"job-{len(store.all()) + 1:04d}"
    record = {"id": job_id, "name": name, "created": store.tick(), "state": "pending"}
    store.put(record)
    return job_id
''',
    "scheduler": '''"""Picks the next job to run."""


def next_job(store):
    pending = [r for r in store.all() if r["state"] == "pending"]
    if not pending:
        return None
    job = min(pending, key=lambda r: r["created"])
    return store.update(job["id"], state="running")
''',
    "api": '''"""Read-only API views."""

FIELDS = ("id", "name", "state")


def job_view(store, job_id):
    record = store.get(job_id)
    if record is None:
        raise KeyError(job_id)
    return {field: record[field] for field in FIELDS}
''',
    "cli": '''"""Terminal output."""


def format_row(record):
    return f"{record['id']}  {record['state']:<8} {record['name']}"
''',
    "exporter": '''"""CSV export."""
import csv
import io

COLUMNS = ["id", "name", "state"]


def export_csv(store):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(COLUMNS)
    for record in store.all():
        writer.writerow([record[c] for c in COLUMNS])
    return out.getvalue()
''',
    "metrics": '''"""Counters for the dashboard."""
from collections import Counter


def counts_by_state(store):
    return dict(Counter(r["state"] for r in store.all()))
''',
    "archive": '''"""Compact one-line archive format."""


def pack(record):
    return "|".join([record["id"], record["name"], record["state"], str(record["created"])])


def unpack(line):
    job_id, name, state, created = line.split("|")
    return {"id": job_id, "name": name, "state": state, "created": int(created)}
''',
}

VISIBLE_TEST = '''import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import api, producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402


class TestJobs(unittest.TestCase):
    def setUp(self):
        self.store = Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))

    def test_fifo(self):
        a = producer.submit(self.store, "a")
        b = producer.submit(self.store, "b")
        self.assertEqual(scheduler.next_job(self.store)["id"], a)
        self.assertEqual(scheduler.next_job(self.store)["id"], b)
        self.assertIsNone(scheduler.next_job(self.store))

    def test_view(self):
        a = producer.submit(self.store, "build")
        self.assertEqual(api.job_view(self.store, a)["name"], "build")


if __name__ == "__main__":
    unittest.main()
'''

CONTRACT = {
    "producer": "`producer.submit(store, name, priority=\"normal\")` accepts `\"low\"`, "
                "`\"normal\"` or `\"high\"` and raises `ValueError` for anything else. "
                "Existing calls without `priority` keep working.",
    "scheduler": "`scheduler.next_job(store)` returns the highest-priority pending job; "
                 "ties go to the oldest.",
    "api": "`api.job_view(store, job_id)` includes `\"priority\"`, with the value given at "
           "submission (e.g. `\"high\"`).",
    "cli": "`cli.format_row(record)` starts with the priority in capitals in brackets, "
           "e.g. `[HIGH] job-0001  pending  build`.",
    "exporter": "`exporter.export_csv(store)` has a `priority` column holding "
                "`low`/`normal`/`high`.",
    "metrics": "`metrics.counts_by_priority(store)` returns "
               "`{\"low\": n, \"normal\": n, \"high\": n}`, all three keys always present.",
    "archive": "`archive.unpack(archive.pack(record))` preserves the job's priority.",
}

INSTRUCTION = """\
Add job priorities to the job system in `jobs/`.

Required behaviour:

{contract}

Jobs submitted before this change have no priority. Treat them as `normal` everywhere.

Files that need changes: {files}. `python -m unittest discover tests` must keep passing.
"""


CORE_CHECKS = ("check_order", "check_view", "check_cli", "check_invalid", "check_legacy",
               "check_regression")
EXTRA_CHECKS = {"exporter": "check_export", "metrics": "check_metrics", "archive": "check_archive"}


def _items(size):
    return list(CORE) + list(EXTRA[: size - len(CORE)])


def _codec(key, enc):
    table = ENCODINGS[enc]
    return (
        f"_KEY = {key!r}\n"
        f"_ENCODE = {json.dumps(table)}\n"
        "_DECODE = {v: k for k, v in _ENCODE.items()}\n"
        "_RANK = {'low': 0, 'normal': 1, 'high': 2}\n\n\n"
        "def _priority(record):\n"
        "    value = record.get(_KEY)\n"
        "    return 'normal' if value is None else _DECODE.get(value, 'normal')\n"
    )


def render_module(module, key="priority", enc="str"):
    """A correct implementation of `module` under one record representation.

    Used by the oracle solution (one representation everywhere) and by the
    rehearsal's eager fan-out policy (a different one per worker).
    """
    codec = _codec(key, enc)
    if module == "producer":
        return (
            '"""Job submission."""\n' + codec + "\n\n"
            "def submit(store, name, priority=\"normal\"):\n"
            "    if priority not in _ENCODE:\n"
            "        raise ValueError(f\"unknown priority {priority!r}\")\n"
            "    job_id = f\"job-{len(store.all()) + 1:04d}\"\n"
            "    record = {\"id\": job_id, \"name\": name, \"created\": store.tick(),\n"
            "              \"state\": \"pending\", _KEY: _ENCODE[priority]}\n"
            "    store.put(record)\n"
            "    return job_id\n"
        )
    if module == "scheduler":
        return (
            '"""Picks the next job to run."""\n' + codec + "\n\n"
            "def next_job(store):\n"
            "    pending = [r for r in store.all() if r[\"state\"] == \"pending\"]\n"
            "    if not pending:\n"
            "        return None\n"
            "    job = min(pending, key=lambda r: (-_RANK[_priority(r)], r[\"created\"]))\n"
            "    return store.update(job[\"id\"], state=\"running\")\n"
        )
    if module == "api":
        return (
            '"""Read-only API views."""\n' + codec + "\n"
            "FIELDS = (\"id\", \"name\", \"state\")\n\n\n"
            "def job_view(store, job_id):\n"
            "    record = store.get(job_id)\n"
            "    if record is None:\n"
            "        raise KeyError(job_id)\n"
            "    view = {field: record[field] for field in FIELDS}\n"
            "    view[\"priority\"] = _priority(record)\n"
            "    return view\n"
        )
    if module == "cli":
        return (
            '"""Terminal output."""\n' + codec + "\n\n"
            "def format_row(record):\n"
            "    tag = f\"[{_priority(record).upper()}]\"\n"
            "    return f\"{tag} {record['id']}  {record['state']:<8} {record['name']}\"\n"
        )
    if module == "exporter":
        return (
            '"""CSV export."""\nimport csv\nimport io\n\n' + codec + "\n"
            "COLUMNS = [\"id\", \"name\", \"state\", \"priority\"]\n\n\n"
            "def export_csv(store):\n"
            "    out = io.StringIO()\n"
            "    writer = csv.writer(out)\n"
            "    writer.writerow(COLUMNS)\n"
            "    for record in store.all():\n"
            "        writer.writerow([record[\"id\"], record[\"name\"], record[\"state\"],\n"
            "                         _priority(record)])\n"
            "    return out.getvalue()\n"
        )
    if module == "metrics":
        return (
            '"""Counters for the dashboard."""\nfrom collections import Counter\n\n' + codec + "\n\n"
            "def counts_by_state(store):\n"
            "    return dict(Counter(r[\"state\"] for r in store.all()))\n\n\n"
            "def counts_by_priority(store):\n"
            "    counts = {\"low\": 0, \"normal\": 0, \"high\": 0}\n"
            "    for record in store.all():\n"
            "        counts[_priority(record)] += 1\n"
            "    return counts\n"
        )
    if module == "archive":
        return (
            '"""Compact one-line archive format."""\n' + codec + "\n\n"
            "def pack(record):\n"
            "    return \"|\".join([record[\"id\"], record[\"name\"], record[\"state\"],\n"
            "                     str(record[\"created\"]), _priority(record)])\n\n\n"
            "def unpack(line):\n"
            "    job_id, name, state, created, priority = line.split(\"|\")\n"
            "    return {\"id\": job_id, \"name\": name, \"state\": state,\n"
            "            \"created\": int(created), _KEY: _ENCODE[priority]}\n"
        )
    raise KeyError(module)


# Hidden integration checks. Pure stdlib; imported by the verifier with the
# workspace on sys.path. Each check is one point.
HIDDEN = '''"""Hidden integration checks for family C. One point each."""
import csv
import io
import os
import tempfile


def _fresh():
    from jobs.store import Store
    return Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))


def _seed(store):
    from jobs import producer
    ids = {}
    ids["low"] = producer.submit(store, "lint", priority="low")
    ids["normal1"] = producer.submit(store, "build", priority="normal")
    ids["high"] = producer.submit(store, "deploy", priority="high")
    ids["normal2"] = producer.submit(store, "test")
    return ids


def _legacy(store):
    store.put({"id": "job-0900", "name": "old", "created": store.tick(), "state": "pending"})
    return "job-0900"


def check_order():
    from jobs import scheduler
    store = _fresh()
    ids = _seed(store)
    got = [scheduler.next_job(store)["id"] for _ in range(4)]
    assert got == [ids["high"], ids["normal1"], ids["normal2"], ids["low"]], got


def check_view():
    from jobs import api
    store = _fresh()
    ids = _seed(store)
    for level, job in (("low", ids["low"]), ("high", ids["high"]), ("normal", ids["normal2"])):
        assert api.job_view(store, job)["priority"] == level


def check_cli():
    from jobs import cli
    store = _fresh()
    ids = _seed(store)
    assert cli.format_row(store.get(ids["high"])).startswith("[HIGH]")
    assert cli.format_row(store.get(ids["low"])).startswith("[LOW]")
    assert cli.format_row(store.get(ids["normal2"])).startswith("[NORMAL]")


def check_invalid():
    from jobs import producer
    store = _fresh()
    try:
        producer.submit(store, "x", priority="urgent")
    except ValueError:
        return
    raise AssertionError("no ValueError")


def check_legacy():
    from jobs import api, cli, scheduler
    store = _fresh()
    old = _legacy(store)
    ids = _seed(store)
    assert api.job_view(store, old)["priority"] == "normal"
    assert cli.format_row(store.get(old)).startswith("[NORMAL]")
    got = [scheduler.next_job(store)["id"] for _ in range(5)]
    assert got[0] == ids["high"] and got[-1] == ids["low"], got
    assert got.index(old) < got.index(ids["normal1"]), got


def check_export():
    from jobs import exporter
    store = _fresh()
    ids = _seed(store)
    rows = {r["id"]: r for r in csv.DictReader(io.StringIO(exporter.export_csv(store)))}
    assert rows[ids["high"]]["priority"] == "high"
    assert rows[ids["normal2"]]["priority"] == "normal"


def check_metrics():
    from jobs import metrics
    store = _fresh()
    _legacy(store)
    _seed(store)
    assert metrics.counts_by_priority(store) == {"low": 1, "normal": 3, "high": 1}


def check_archive():
    from jobs import api, archive, scheduler
    store = _fresh()
    ids = _seed(store)
    other = _fresh()
    for record in store.all():
        other.put(archive.unpack(archive.pack(record)))
    assert api.job_view(other, ids["high"])["priority"] == "high"
    assert scheduler.next_job(other)["id"] == ids["high"]


def check_regression():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"],
                            cwd=os.environ.get("ORCH_WORKSPACE", "/workspace"),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-500:]

'''


def generate(size, seed):
    if size not in SIZES:
        raise ValueError(f"C sizes are {SIZES}")
    rng = rng_for(FAMILY, size, seed)
    modules = _items(size)
    files = {"jobs/__init__.py": "", "jobs/store.py": STORE, "tests/test_jobs.py": VISIBLE_TEST}
    for module in CORE + EXTRA:
        if module in modules:
            files[f"jobs/{module}.py"] = BASE[module]
    contract = "\n".join(f"- {CONTRACT[m]}" for m in modules)
    checks = list(CORE_CHECKS) + [EXTRA_CHECKS[m] for m in modules if m in EXTRA]
    solution = "".join(
        f"cat > jobs/{m}.py <<'PYEOF'\n{render_module(m)}PYEOF\n" for m in modules
    )
    # Seed only perturbs file ordering in the instruction; C is a control family
    # whose value is its shape, not contamination resistance.
    order = list(modules)
    rng.shuffle(order)
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=SOLO,
        instruction=INSTRUCTION.format(
            contract=contract, files=", ".join(f"`jobs/{m}.py`" for m in order)
        ),
        files=files,
        truth={"checks": checks, "modules": modules},
        solution=solution,
        work_items=modules,
        hidden_tests={"hidden_checks.py": HIDDEN},
    )
