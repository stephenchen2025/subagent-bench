"""C -- coupled views. Decomposes cleanly, but only behind a contract.

Add job priorities to a small job system, then make each of M "views" (email
digest, pager line, dashboard tile, ...) show a job's priority the way its own
spec in docs/views/<view>.md says. The views are independent of each other and
the instruction lists them, so the work splits naturally: a few views per
worker. At M=40 the specs, modules and the code written for them overflow a 32k window, and a
solo agent needs well over 100 steps.

The catch: every view reads the job record the producer writes, and the
instruction deliberately says nothing about how priority is stored in it. One
agent makes that choice once without noticing. Isolated workers each make it
separately -- one stores "priority": "high", another reads record.get("prio", 1)
-- and each view is locally correct while the integration checks fail. That is
Cognition's Flappy Bird failure, and MAST's inter-agent misalignment.

So the right policy is to delegate *behind a contract*: fix the record format
first and put it in every brief. The oracle plan does exactly that. Delegating
without it is the failure this family exists to catch.
"""

import json

from orch.task import DELEGATE, OrchTask, rng_for, task_id

FAMILY = "C"
SIZES = (20, 30, 40)
VIEWS_PER_WORKER = 3

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
CONTRACT = ("Store priority in the job record under the key 'priority' as one of the "
            "strings 'low', 'normal' or 'high'. A record without that key is 'normal'.")

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

VIEW_NAMES = [
    "email_digest", "slack_alert", "sms_brief", "dashboard_tile", "pager_line", "audit_row",
    "csv_line", "rss_item", "webhook_payload", "kanban_card", "cli_table", "weekly_report",
    "status_badge", "ops_ticker", "mobile_push", "tv_wall", "chat_bot", "voice_prompt",
    "calendar_note", "log_line", "json_feed", "html_row", "markdown_list", "jira_comment",
    "teams_card", "discord_embed", "grafana_note", "sheet_row", "printer_slip", "kiosk_screen",
    "watch_face", "desktop_toast", "email_subject", "invoice_note", "archive_label",
    "qa_checklist", "oncall_digest", "wiki_table", "exec_summary", "sla_board",
]

# How each view shows a level. Tokens are delimited by one space, so a check can
# tell "*" from "**".
STYLES = {
    "bracket": {"high": "[HIGH]", "normal": "[NORMAL]", "low": "[LOW]"},
    "p_number": {"high": "P1", "normal": "P2", "low": "P3"},
    "stars": {"high": "***", "normal": "**", "low": "*"},
    "bangs": {"high": "!!!", "normal": "!!", "low": "!"},
    "color": {"high": "color=red", "normal": "color=amber", "low": "color=green"},
    "word": {"high": "priority:high", "normal": "priority:normal", "low": "priority:low"},
    "level": {"high": "level=3", "normal": "level=2", "low": "level=1"},
    "arrows": {"high": "^^", "normal": "--", "low": "vv"},
    "urgency": {"high": "URGENT", "normal": "ROUTINE", "low": "DEFERRABLE"},
}
# (python expression over `record`, human description)
LAYOUTS = [
    ("f\"{record['id']} | {record['name']} | {record['state']}\"", "id | name | state"),
    ("f\"{record['name']} ({record['id']}) is {record['state']}\"", "name (id) is state"),
    ("f\"{record['state'].upper()}: {record['name']} [{record['id']}]\"", "STATE: name [id]"),
    ("f\"{record['id']}: {record['name']} -- {record['state']}\"", "id: name -- state"),
    ("f\"job {record['id']} / {record['name']} / {record['state']}\"", "job id / name / state"),
]
AUDIENCES = [
    "the on-call engineer who is paged at night", "the finance team's weekly review",
    "customer support leads", "the platform team's wall display", "release managers",
    "auditors reviewing job history", "the executive summary email", "mobile users",
]
HISTORY = [
    "Switched from a fixed-width layout after complaints about truncation on small screens.",
    "Added the state column; before that the view only showed the job name.",
    "Moved from the legacy notifier into views/ as part of the views consolidation.",
    "Owners asked that the format stay stable because downstream parsers depend on it.",
    "Localisation was considered and deferred; everything is English for now.",
    "A request to add colours in the terminal was declined to keep output plain text.",
    "Renamed from its old module name; the old name is gone.",
    "The layout was reviewed with the design team; keep separators exactly as they are.",
]


EXAMPLE_JOBS = ["nightly-backup", "invoice-run", "reindex-search", "rotate-keys",
                "send-digest", "purge-cache", "export-ledger", "resize-images",
                "sync-inventory", "compact-logs", "renew-certs", "rebuild-feed"]


def _example_line(params, job_id, name, state, level):
    record = {"id": job_id, "name": name, "state": state}
    base = eval("lambda record: " + LAYOUTS[params["layout"]][0])(record)  # noqa: S307
    token = STYLES[params["style"]][level]
    return f"{token} {base}" if params["position"] == "prefix" else f"{base} {token}"


def _view_params(rng, size):
    names = rng.sample(VIEW_NAMES, size)
    styles = list(STYLES)
    views = {}
    for i, name in enumerate(names):
        views[name] = {
            "style": styles[i] if i < len(styles) else rng.choice(styles),
            "position": rng.choice(["prefix", "suffix"]),
            "layout": rng.randrange(len(LAYOUTS)),
            "audience": rng.choice(AUDIENCES),
            "history": rng.sample(HISTORY, 8),
            "examples": [(f"job-{rng.randint(1, 999):04d}", rng.choice(EXAMPLE_JOBS),
                          rng.choice(["pending", "running", "done", "failed"]),
                          rng.choice(LEVELS)) for _ in range(14)],
        }
    return views


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


BASE_CORE = {
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
}


def render_core(module, key="priority", enc="str"):
    """A correct producer or scheduler under one record representation."""
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
    raise KeyError(module)


def _title(name):
    return name.replace("_", " ")


def base_view(name, params):
    expr = LAYOUTS[params["layout"]][0]
    return (
        f'"""The {_title(name)} view: one line per job, for {params["audience"]}."""\n\n\n'
        "def render(record):\n"
        f"    return {expr}\n"
    )


def render_view(name, params, key="priority", enc="str"):
    """A correct implementation of one view under one record representation."""
    expr = LAYOUTS[params["layout"]][0]
    tokens = STYLES[params["style"]]
    joined = 'f"{token} {base}"' if params["position"] == "prefix" else 'f"{base} {token}"'
    return (
        f'"""The {_title(name)} view: one line per job, for {params["audience"]}."""\n'
        + _codec(key, enc) + "\n"
        f"_TOKENS = {json.dumps(tokens)}\n\n\n"
        "def render(record):\n"
        f"    base = {expr}\n"
        "    token = _TOKENS[_priority(record)]\n"
        f"    return {joined}\n"
    )


def view_spec(name, params):
    tokens = STYLES[params["style"]]
    where = ("at the start of the line, followed by one space" if params["position"] == "prefix"
             else "at the end of the line, after one space")
    history = "\n".join(f"- {h}" for h in params["history"])
    examples = "\n".join(
        f"| {job} | {name} | {state} | {level} | `{_example_line(params, job, name, state, level)}` |"
        for job, name, state, level in params["examples"])
    return f"""# {_title(name).title()} view

Module: `views/{name}.py`. Audience: {params["audience"]}.

Current layout: `{LAYOUTS[params["layout"]][1]}`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority {where}:

| priority | marker |
|---|---|
| high | `{tokens["high"]}` |
| normal | `{tokens["normal"]}` |
| low | `{tokens["low"]}` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
{examples}

## History

{history}

## Owners

Questions about this view go to the team that consumes it ({params["audience"]}).
Changes to the layout itself need their sign-off; adding the priority marker does not.
"""


VISIBLE_TEST = '''import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = {views!r}


class TestJobs(unittest.TestCase):
    def setUp(self):
        self.store = Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))

    def test_fifo(self):
        a = producer.submit(self.store, "a")
        b = producer.submit(self.store, "b")
        self.assertEqual(scheduler.next_job(self.store)["id"], a)
        self.assertEqual(scheduler.next_job(self.store)["id"], b)

    def test_views_show_id_and_name(self):
        job = producer.submit(self.store, "build")
        for view in VIEWS:
            line = importlib.import_module(f"views.{{view}}").render(self.store.get(job))
            self.assertIn(job, line)
            self.assertIn("build", line)


if __name__ == "__main__":
    unittest.main()
'''

HIDDEN = '''"""Hidden integration checks for family C. One point each."""
import importlib
import os
import tempfile

VIEWS = {views!r}


def _fresh():
    from jobs.store import Store
    return Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))


def _seed(store):
    from jobs import producer
    return {{
        "low": producer.submit(store, "lint", priority="low"),
        "normal": producer.submit(store, "build", priority="normal"),
        "high": producer.submit(store, "deploy", priority="high"),
        "default": producer.submit(store, "test"),
    }}


def _legacy(store):
    store.put({{"id": "job-0900", "name": "old", "created": store.tick(), "state": "pending"}})
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
'''

CORE_CHECKS = ("check_order", "check_invalid", "check_legacy_order", "check_regression")

INSTRUCTION = """\
Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the {m} views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: {views}.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
"""

WORKER_BRIEF = """\
Add a priority marker to these views: {files}. For each view, the exact marker and
where it goes are in its spec, `docs/views/<view>.md`. Change nothing else about a
view's output, and edit no other files.

Record contract: {contract}

When you are done, run `python -m unittest discover tests` and report which views
you changed and whether the tests pass.
"""

CORE_BRIEF = """\
Add job priorities to `jobs/producer.py` and `jobs/scheduler.py`, and edit no other files.

- `submit(store, name, priority="normal")` accepts "low", "normal" or "high" and raises
  ValueError for anything else; existing calls without priority keep working.
- `next_job(store)` returns the highest-priority pending job; ties go to the oldest.
- Jobs without a priority count as "normal".

Record contract: {contract}

Run `python -m unittest discover tests` and report the result.
"""


def generate(size, seed):
    if size < 8:
        raise ValueError("C needs at least 8 views to be a long-horizon task")
    rng = rng_for(FAMILY, size, seed)
    views = _view_params(rng, size)
    names = list(views)
    files = {
        "jobs/__init__.py": "",
        "jobs/store.py": STORE,
        "jobs/producer.py": BASE_CORE["producer"],
        "jobs/scheduler.py": BASE_CORE["scheduler"],
        "views/__init__.py": "",
        "tests/test_jobs.py": VISIBLE_TEST.format(views=names),
    }
    for name, params in views.items():
        files[f"views/{name}.py"] = base_view(name, params)
        files[f"docs/views/{name}.md"] = view_spec(name, params)
    hidden_views = {
        n: {"tokens": STYLES[p["style"]], "position": p["position"],
            "expr": LAYOUTS[p["layout"]][0]}
        for n, p in views.items()
    }
    solution = "".join(
        f"cat > jobs/{m}.py <<'PYEOF'\n{render_core(m)}PYEOF\n" for m in ("producer", "scheduler")
    ) + "".join(
        f"cat > views/{n}.py <<'PYEOF'\n{render_view(n, p)}PYEOF\n" for n, p in views.items()
    )
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=DELEGATE,
        instruction=INSTRUCTION.format(m=size, views=", ".join(f"`{n}`" for n in names)),
        files=files,
        truth={"checks": list(CORE_CHECKS) + [f"check_view_{n}" for n in names],
               "views": views},
        solution=solution,
        work_items=names,
        oracle_plan=plan(names),
        hidden_tests={"hidden_checks.py": HIDDEN.format(views=hidden_views)},
    )


def plan(names, contract=CONTRACT):
    """The ideal decomposition: the core, then views in groups; the contract in every brief."""
    groups = [names[i:i + VIEWS_PER_WORKER] for i in range(0, len(names), VIEWS_PER_WORKER)]
    return [{"items": [], "brief": CORE_BRIEF.format(contract=contract)}] + [
        {"items": g, "brief": WORKER_BRIEF.format(
            files=", ".join(f"views/{n}.py" for n in g), contract=contract)}
        for g in groups
    ]


def views_in(text):
    """View names a brief or instruction mentions, in order."""
    import re

    return re.findall(r"views/(\w+)\.py", text)
