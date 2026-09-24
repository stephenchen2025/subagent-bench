"""Hidden integration checks for family C. One point each."""
import importlib
import os
import tempfile

VIEWS = {'jira_comment': {'tokens': {'high': '[HIGH]', 'normal': '[NORMAL]', 'low': '[LOW]'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'invoice_note': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'csv_line': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'exec_summary': {'tokens': {'high': '!!!', 'normal': '!!', 'low': '!'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'printer_slip': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'wiki_table': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'suffix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'teams_card': {'tokens': {'high': 'level=3', 'normal': 'level=2', 'low': 'level=1'}, 'position': 'suffix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'archive_label': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'prefix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'discord_embed': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'suffix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'sms_brief': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'qa_checklist': {'tokens': {'high': '[HIGH]', 'normal': '[NORMAL]', 'low': '[LOW]'}, 'position': 'suffix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'cli_table': {'tokens': {'high': 'level=3', 'normal': 'level=2', 'low': 'level=1'}, 'position': 'prefix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'markdown_list': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'mobile_push': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'webhook_payload': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'tv_wall': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'desktop_toast': {'tokens': {'high': '[HIGH]', 'normal': '[NORMAL]', 'low': '[LOW]'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'html_row': {'tokens': {'high': '[HIGH]', 'normal': '[NORMAL]', 'low': '[LOW]'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'slack_alert': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'prefix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'kiosk_screen': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'suffix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}}


def _fresh():
    from jobs.store import Store
    return Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))


def _seed(store):
    from jobs import producer
    return {
        "low": producer.submit(store, "lint", priority="low"),
        "normal": producer.submit(store, "build", priority="normal"),
        "high": producer.submit(store, "deploy", priority="high"),
        "default": producer.submit(store, "test"),
    }


def _legacy(store):
    store.put({"id": "job-0900", "name": "old", "created": store.tick(), "state": "pending"})
    return "job-0900"


def check_order():
    from jobs import scheduler
    store = _fresh()
    ids = _seed(store)
    got = [scheduler.next_job(store)["id"] for _ in range(4)]
    assert got == [ids["high"], ids["normal"], ids["default"], ids["low"]], got


def check_invalid():
    from jobs import producer
    try:
        producer.submit(_fresh(), "x", priority="urgent")
    except ValueError:
        return
    raise AssertionError("no ValueError")


def check_legacy_order():
    from jobs import scheduler
    store = _fresh()
    old = _legacy(store)
    ids = _seed(store)
    got = [scheduler.next_job(store)["id"] for _ in range(5)]
    assert got[0] == ids["high"] and got[-1] == ids["low"], got
    assert got.index(old) < got.index(ids["normal"]), got


def check_regression():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"],
                            cwd=os.environ.get("ORCH_WORKSPACE", "/workspace"),
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr[-500:]


def _view_check(name, spec):
    base = eval("lambda record: " + spec["expr"])  # noqa: S307 -- our own layouts

    def check():
        view = importlib.import_module("views." + name)
        store = _fresh()
        old = _legacy(store)
        ids = _seed(store)
        cases = [(ids["high"], "high"), (ids["normal"], "normal"), (ids["low"], "low"),
                 (ids["default"], "normal"), (old, "normal")]
        for job, level in cases:
            record = store.get(job)
            line = view.render(record)
            token = spec["tokens"][level]
            if spec["position"] == "prefix":
                assert line.startswith(token + " "), (line, token)
                rest = line[len(token) + 1:]
            else:
                assert line.endswith(" " + token), (line, token)
                rest = line[:-(len(token) + 1)]
            assert rest == base(record), (rest, line)
    return check


for _name, _spec in VIEWS.items():
    globals()["check_view_" + _name] = _view_check(_name, _spec)
