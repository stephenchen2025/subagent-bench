"""Hidden integration checks for family C. One point each."""
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

