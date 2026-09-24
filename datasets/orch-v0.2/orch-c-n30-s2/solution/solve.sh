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
cat > views/cli_table.py <<'PYEOF'
"""The cli table view: one line per job, for the finance team's weekly review."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "[HIGH]", "normal": "[NORMAL]", "low": "[LOW]"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/jira_comment.py <<'PYEOF'
"""The jira comment view: one line per job, for mobile users."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "P1", "normal": "P2", "low": "P3"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/discord_embed.py <<'PYEOF'
"""The discord embed view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "***", "normal": "**", "low": "*"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/sla_board.py <<'PYEOF'
"""The sla board view: one line per job, for the executive summary email."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/dashboard_tile.py <<'PYEOF'
"""The dashboard tile view: one line per job, for the executive summary email."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "color=red", "normal": "color=amber", "low": "color=green"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/invoice_note.py <<'PYEOF'
"""The invoice note view: one line per job, for the finance team's weekly review."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "priority:high", "normal": "priority:normal", "low": "priority:low"}


def render(record):
    base = f"{record['id']}: {record['name']} -- {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/html_row.py <<'PYEOF'
"""The html row view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "level=3", "normal": "level=2", "low": "level=1"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/mobile_push.py <<'PYEOF'
"""The mobile push view: one line per job, for the platform team's wall display."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "^^", "normal": "--", "low": "vv"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/calendar_note.py <<'PYEOF'
"""The calendar note view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "URGENT", "normal": "ROUTINE", "low": "DEFERRABLE"}


def render(record):
    base = f"job {record['id']} / {record['name']} / {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/status_badge.py <<'PYEOF'
"""The status badge view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "level=3", "normal": "level=2", "low": "level=1"}


def render(record):
    base = f"job {record['id']} / {record['name']} / {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/ops_ticker.py <<'PYEOF'
"""The ops ticker view: one line per job, for the platform team's wall display."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "***", "normal": "**", "low": "*"}


def render(record):
    base = f"job {record['id']} / {record['name']} / {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/webhook_payload.py <<'PYEOF'
"""The webhook payload view: one line per job, for the platform team's wall display."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "color=red", "normal": "color=amber", "low": "color=green"}


def render(record):
    base = f"{record['id']}: {record['name']} -- {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/sheet_row.py <<'PYEOF'
"""The sheet row view: one line per job, for the finance team's weekly review."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/kiosk_screen.py <<'PYEOF'
"""The kiosk screen view: one line per job, for the finance team's weekly review."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['id']}: {record['name']} -- {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/email_digest.py <<'PYEOF'
"""The email digest view: one line per job, for customer support leads."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "[HIGH]", "normal": "[NORMAL]", "low": "[LOW]"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/markdown_list.py <<'PYEOF'
"""The markdown list view: one line per job, for customer support leads."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/printer_slip.py <<'PYEOF'
"""The printer slip view: one line per job, for the finance team's weekly review."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "***", "normal": "**", "low": "*"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/voice_prompt.py <<'PYEOF'
"""The voice prompt view: one line per job, for customer support leads."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "priority:high", "normal": "priority:normal", "low": "priority:low"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/slack_alert.py <<'PYEOF'
"""The slack alert view: one line per job, for the executive summary email."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "URGENT", "normal": "ROUTINE", "low": "DEFERRABLE"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/log_line.py <<'PYEOF'
"""The log line view: one line per job, for mobile users."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "URGENT", "normal": "ROUTINE", "low": "DEFERRABLE"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/grafana_note.py <<'PYEOF'
"""The grafana note view: one line per job, for the executive summary email."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "***", "normal": "**", "low": "*"}


def render(record):
    base = f"job {record['id']} / {record['name']} / {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/rss_item.py <<'PYEOF'
"""The rss item view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "color=red", "normal": "color=amber", "low": "color=green"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/archive_label.py <<'PYEOF'
"""The archive label view: one line per job, for the on-call engineer who is paged at night."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "color=red", "normal": "color=amber", "low": "color=green"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/sms_brief.py <<'PYEOF'
"""The sms brief view: one line per job, for the executive summary email."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/oncall_digest.py <<'PYEOF'
"""The oncall digest view: one line per job, for mobile users."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"{record['id']} | {record['name']} | {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/pager_line.py <<'PYEOF'
"""The pager line view: one line per job, for mobile users."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "^^", "normal": "--", "low": "vv"}


def render(record):
    base = f"{record['id']}: {record['name']} -- {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/desktop_toast.py <<'PYEOF'
"""The desktop toast view: one line per job, for mobile users."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "URGENT", "normal": "ROUTINE", "low": "DEFERRABLE"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/audit_row.py <<'PYEOF'
"""The audit row view: one line per job, for the on-call engineer who is paged at night."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "!!!", "normal": "!!", "low": "!"}


def render(record):
    base = f"job {record['id']} / {record['name']} / {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
cat > views/wiki_table.py <<'PYEOF'
"""The wiki table view: one line per job, for customer support leads."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "[HIGH]", "normal": "[NORMAL]", "low": "[LOW]"}


def render(record):
    base = f"{record['name']} ({record['id']}) is {record['state']}"
    token = _TOKENS[_priority(record)]
    return f"{base} {token}"
PYEOF
cat > views/csv_line.py <<'PYEOF'
"""The csv line view: one line per job, for auditors reviewing job history."""
_KEY = 'priority'
_ENCODE = {"low": "low", "normal": "normal", "high": "high"}
_DECODE = {v: k for k, v in _ENCODE.items()}
_RANK = {'low': 0, 'normal': 1, 'high': 2}


def _priority(record):
    value = record.get(_KEY)
    return 'normal' if value is None else _DECODE.get(value, 'normal')

_TOKENS = {"high": "[HIGH]", "normal": "[NORMAL]", "low": "[LOW]"}


def render(record):
    base = f"{record['state'].upper()}: {record['name']} [{record['id']}]"
    token = _TOKENS[_priority(record)]
    return f"{token} {base}"
PYEOF
