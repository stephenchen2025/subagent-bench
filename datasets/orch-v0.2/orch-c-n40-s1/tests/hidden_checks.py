"""Hidden integration checks for family C. One point each."""
import importlib
import os
import tempfile

VIEWS = {'pager_line': {'tokens': {'high': '[HIGH]', 'normal': '[NORMAL]', 'low': '[LOW]'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'rss_item': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'chat_bot': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'status_badge': {'tokens': {'high': '!!!', 'normal': '!!', 'low': '!'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'mobile_push': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'json_feed': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'suffix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'qa_checklist': {'tokens': {'high': 'level=3', 'normal': 'level=2', 'low': 'level=1'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'exec_summary': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'wiki_table': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'log_line': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'grafana_note': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'voice_prompt': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'discord_embed': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'sheet_row': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'kiosk_screen': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'csv_line': {'tokens': {'high': '!!!', 'normal': '!!', 'low': '!'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'sla_board': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'ops_ticker': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'teams_card': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'printer_slip': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'archive_label': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'prefix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'email_digest': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'oncall_digest': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'watch_face': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'dashboard_tile': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'sms_brief': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'invoice_note': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'prefix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'audit_row': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'desktop_toast': {'tokens': {'high': 'level=3', 'normal': 'level=2', 'low': 'level=1'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'cli_table': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'email_subject': {'tokens': {'high': '!!!', 'normal': '!!', 'low': '!'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']} | {record[\'name\']} | {record[\'state\']}"'}, 'tv_wall': {'tokens': {'high': 'priority:high', 'normal': 'priority:normal', 'low': 'priority:low'}, 'position': 'suffix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'markdown_list': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'suffix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}, 'jira_comment': {'tokens': {'high': 'URGENT', 'normal': 'ROUTINE', 'low': 'DEFERRABLE'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'slack_alert': {'tokens': {'high': '^^', 'normal': '--', 'low': 'vv'}, 'position': 'suffix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'kanban_card': {'tokens': {'high': '***', 'normal': '**', 'low': '*'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'webhook_payload': {'tokens': {'high': 'level=3', 'normal': 'level=2', 'low': 'level=1'}, 'position': 'prefix', 'expr': 'f"{record[\'state\'].upper()}: {record[\'name\']} [{record[\'id\']}]"'}, 'weekly_report': {'tokens': {'high': 'color=red', 'normal': 'color=amber', 'low': 'color=green'}, 'position': 'suffix', 'expr': 'f"job {record[\'id\']} / {record[\'name\']} / {record[\'state\']}"'}, 'html_row': {'tokens': {'high': 'P1', 'normal': 'P2', 'low': 'P3'}, 'position': 'prefix', 'expr': 'f"{record[\'id\']}: {record[\'name\']} -- {record[\'state\']}"'}, 'calendar_note': {'tokens': {'high': '!!!', 'normal': '!!', 'low': '!'}, 'position': 'prefix', 'expr': 'f"{record[\'name\']} ({record[\'id\']}) is {record[\'state\']}"'}}


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
