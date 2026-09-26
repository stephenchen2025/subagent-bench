#!/usr/bin/env python3
"""LH14 -- write a parser for each of 32 log formats, graded on held-out logs.

The observability team is moving 32 legacy services onto one log schema:

    {"ts": "2026-09-14T02:09:12.345Z", "level": "INFO"|"WARN"|"ERROR"|"DEBUG",
     "message": "...", "request_id": "..." or null}

For each format there is a sample (samples/<fmt>.log) and, for half of them, a
format note (docs/formats/<fmt>.md). The deliverable is parsers/<fmt>.py with
`parse(text) -> list[dict]`. The grader runs every parser on HELD-OUT log text
from the same service and compares the records.

Formats are combinations of six timestamp styles (UTC ISO, ISO with an offset,
epoch milliseconds, Apache CLF with an offset, syslog without a year, a local
"space" style), four level encodings (words, lowercase synonyms including
`warning` and `fatal`, single letters, Python's numeric levels), five layouts
(bracketed, key=value with escaped quotes, JSON with nested fields, pipe, CSV
with doubled quotes), optional multi-line stack traces, and request ids that
are sometimes absent. No two formats share all of them, so no parser is
reusable as-is.

    python3 lh14_log_parsers.py --seed 1 --out /fixture
"""

import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

N_FORMATS = 32
TS = ["iso_z", "iso_offset", "epoch_ms", "clf", "syslog", "space"]
LEVELS = ["word", "synonym", "letter", "numeric"]
LAYOUTS = ["bracket", "kv", "json", "pipe", "csv"]
CANON = ["DEBUG", "INFO", "WARN", "ERROR"]
WORDS = ["cache", "flush", "request", "handled", "user", "timeout", "retry", "queue", "worker", "commit",
         "shard", "lease", "token", "refresh", "upload", "chunk", "session", "expired", "quota", "exceeded"]
TRACE = ["Traceback (most recent call last):", '  File "/app/svc/handlers.py", line 88, in handle',
         "    return self._dispatch(req)", "ValueError: bad payload"]


def fmt_ts(style, t, offset_h):
    ms = t.microsecond // 1000
    if style == "iso_z":
        return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ms:03d}Z"
    local = t + dt.timedelta(hours=offset_h)
    sign = "+" if offset_h >= 0 else "-"
    if style == "iso_offset":
        return local.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ms:03d}{sign}{abs(offset_h):02d}:00"
    if style == "epoch_ms":
        return str(int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000))
    if style == "clf":
        return local.strftime("%d/%b/%Y:%H:%M:%S ") + f"{sign}{abs(offset_h):02d}00"
    if style == "syslog":
        return t.strftime("%b %d %H:%M:%S")
    return t.strftime("%Y-%m-%d %H:%M:%S,") + f"{ms:03d}"


def canon_ts(style, t):
    """What the parser must produce: UTC, milliseconds, Z. Formats without
    milliseconds give .000."""
    ms = 0 if style in ("clf", "syslog") else t.microsecond // 1000
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{ms:03d}Z"


def fmt_level(style, level, rng):
    if style == "word":
        return level
    if style == "synonym":
        return {"DEBUG": "debug", "INFO": "info", "WARN": rng.choice(["warn", "warning"]),
                "ERROR": rng.choice(["error", "fatal"])}[level]
    if style == "letter":
        return level[0]
    return str({"DEBUG": 10, "INFO": 20, "WARN": 30, "ERROR": 40}[level])


def render(spec, rec, rng):
    ts = fmt_ts(spec["ts"], rec["t"], spec["offset_h"])
    lvl = fmt_level(spec["level"], rec["level"], rng)
    rid, msg = rec["request_id"], rec["message"]
    lay = spec["layout"]
    first, *rest = msg.split("\n")
    if lay == "bracket":
        line = f"{ts} [{lvl}] {'req=' + rid if rid else '-'} {first}"
    elif lay == "pipe":
        line = f"{ts}|{lvl}|{rid or ''}|{first}"
    elif lay == "kv":
        esc = msg.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        line = f'ts="{ts}" level={lvl} msg="{esc}"' + (f" rid={rid}" if rid else "")
        return line
    elif lay == "json":
        obj = {"@timestamp": ts, "severity": lvl, "body": {"text": msg}}
        if rid:
            obj["trace"] = {"id": rid}
        return json.dumps(obj)
    else:  # csv
        esc = msg.replace('"', '""')
        return f'{ts},{lvl},"{esc}",{rid or ""}'
    return "\n".join([line] + [f"    {r}" for r in rest])


def records(rng, n, spec):
    start = dt.datetime(2026, 9, 14, 0, 0, 0) + dt.timedelta(seconds=rng.randint(0, 3600))
    out, t = [], start
    for _ in range(n):
        t += dt.timedelta(milliseconds=rng.randint(5, 4000))
        words = rng.sample(WORDS, rng.randint(3, 7))
        msg = " ".join(words)
        if rng.random() < 0.25:
            msg += f' "{rng.choice(WORDS)}"'
        if spec["layout"] in ("kv", "csv", "json") and rng.random() < 0.2:
            msg += f", {rng.choice(WORDS)}={rng.randint(1, 99)}"
        level = rng.choices(CANON, weights=[2, 8, 3, 2])[0]
        if spec["multiline"] and level == "ERROR" and rng.random() < 0.7:
            msg += "\n" + "\n".join(TRACE)
        rid = f"{rng.randrange(16**8):08x}" if rng.random() < 0.7 else None
        out.append({"t": t, "level": level, "message": msg, "request_id": rid})
    return out


def expected(spec, recs):
    return [{"ts": canon_ts(spec["ts"], r["t"]), "level": r["level"], "message": r["message"],
             "request_id": r["request_id"]} for r in recs]


def plan(seed, n=N_FORMATS):
    rng = rng_for(seed, "plan")
    combos = [(a, b, c) for a in TS for b in LEVELS for c in LAYOUTS]
    rng.shuffle(combos)
    specs, services = [], ["billing", "search", "gateway", "ingest", "auth", "media", "notify", "ledger"]
    for i, (ts, lvl, lay) in enumerate(combos[:n]):
        specs.append({"name": f"{rng.choice(services)}_{lay}_{i:02d}", "ts": ts, "level": lvl, "layout": lay,
                      "offset_h": rng.choice([-5, -4, 1, 2, 3, 9]) if ts in ("iso_offset", "clf") else 0,
                      "multiline": lay in ("bracket", "pipe") and rng.random() < 0.6,
                      "documented": i % 2 == 0})
    return specs


def doc(spec):
    ts_doc = {"iso_z": "ISO 8601 in UTC with milliseconds and a trailing Z",
              "iso_offset": "ISO 8601 local time with milliseconds and a UTC offset",
              "epoch_ms": "Unix epoch milliseconds",
              "clf": "Apache common-log format with a UTC offset, no milliseconds",
              "syslog": "syslog style, UTC, no year (all logs are from 2026) and no milliseconds",
              "space": "`YYYY-MM-DD HH:MM:SS,mmm` in UTC"}[spec["ts"]]
    lvl_doc = {"word": "DEBUG, INFO, WARN, ERROR", "synonym": "lowercase; `warning` means WARN, `fatal` means ERROR",
               "letter": "first letter: D, I, W, E", "numeric": "Python logging numbers: 10, 20, 30, 40"}[spec["level"]]
    return (f"# {spec['name']}\n\n- Timestamp: {ts_doc}.\n- Level: {lvl_doc}.\n- Layout: {spec['layout']}."
            + ("\n- Error records may continue on following indented lines (a stack trace); they belong to "
               "the record's message, joined with newlines, without the indentation." if spec["multiline"] else "")
            + "\n- The request id is optional.\n")


SCHEMA_MD = """# Target schema

`parse(text)` returns one dict per log record, in order:

- `ts`: UTC, `YYYY-MM-DDTHH:MM:SS.mmmZ` (`.000` when the source has no milliseconds)
- `level`: one of `DEBUG`, `INFO`, `WARN`, `ERROR`
- `message`: the full message, unescaped, including any continuation lines
  (joined with `\\n`, with their leading indentation removed)
- `request_id`: the request id as a string, or `null` when the record has none
"""


def generate(seed, out=None):
    specs = plan(seed)
    files = {"docs/SCHEMA.md": SCHEMA_MD, "parsers/__init__.py": ""}
    truth = {"seed": seed, "formats": {}}
    for spec in specs:
        rng = rng_for(seed, "sample", spec["name"])
        recs = records(rng, 220, spec)
        sample = "\n".join(render(spec, r, rng) for r in recs) + "\n"
        files[f"samples/{spec['name']}.log"] = sample
        if spec["documented"]:
            files[f"docs/formats/{spec['name']}.md"] = doc(spec)
        truth["formats"][spec["name"]] = {"spec": spec, "unit_chars": min(len(sample), 20000) + 1500}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def heldout(seed, spec):
    rng = rng_for(seed, "heldout", spec["name"])
    recs = records(rng, 120, spec)
    return "\n".join(render(spec, r, rng) for r in recs) + "\n", expected(spec, recs)


RUNNER = """import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("p", sys.argv[1])
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
print(json.dumps(mod.parse(open(sys.argv[2]).read()), default=str))
"""


def grade(seed, workspace):
    """Per format: the fraction of held-out records the agent's parser returns
    exactly (compared position by position; missing or extra records count as
    wrong). Reward is the mean over formats."""
    truth = generate(seed)
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        runner = Path(tmp) / "run.py"
        runner.write_text(RUNNER)
        for name, info in truth["formats"].items():
            parser = Path(workspace) / "parsers" / f"{name}.py"
            if not parser.exists():
                per[name] = 0.0
                continue
            text, want = heldout(seed, info["spec"])
            log = Path(tmp) / f"{name}.log"
            log.write_text(text)
            try:
                run = subprocess.run([sys.executable, str(runner), str(parser), str(log)],
                                     capture_output=True, text=True, timeout=60)
                got = json.loads(run.stdout) if run.returncode == 0 else []
            except (subprocess.TimeoutExpired, ValueError):
                got = []
            if not isinstance(got, list):
                got = []
            right = sum(1 for g, w in zip(got, want) if g == w)
            per[name] = round(right / max(len(want), len(got)), 4)
    return {"reward": round(sum(per.values()) / len(per), 4), "formats": per}


ORACLE = r'''"""Reference parser generated from the format's specification."""

import datetime as dt
import json
import re

SPEC = __SPEC__
LEVEL = {"DEBUG": "DEBUG", "INFO": "INFO", "WARN": "WARN", "ERROR": "ERROR", "debug": "DEBUG", "info": "INFO",
         "warn": "WARN", "warning": "WARN", "error": "ERROR", "fatal": "ERROR", "D": "DEBUG", "I": "INFO",
         "W": "WARN", "E": "ERROR", "10": "DEBUG", "20": "INFO", "30": "WARN", "40": "ERROR"}


def _ts(s):
    st = SPEC["ts"]
    if st == "iso_z":
        t = dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ")
    elif st == "iso_offset":
        t = dt.datetime.fromisoformat(s).astimezone(dt.timezone.utc).replace(tzinfo=None)
    elif st == "epoch_ms":
        t = dt.datetime(1970, 1, 1) + dt.timedelta(milliseconds=int(s))
    elif st == "clf":
        t = dt.datetime.strptime(s, "%d/%b/%Y:%H:%M:%S %z").astimezone(dt.timezone.utc).replace(tzinfo=None)
    elif st == "syslog":
        t = dt.datetime.strptime("2026 " + s, "%Y %b %d %H:%M:%S")
    else:
        t = dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S,%f")
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"


TS_RE = {"iso_z": r"\S+", "iso_offset": r"\S+", "epoch_ms": r"\d+", "clf": r"\S+ [+-]\d{4}",
         "syslog": r"\w{3} \d\d \d\d:\d\d:\d\d", "space": r"\S+ \S+"}[SPEC["ts"]]


def parse(text):
    out = []
    lay = SPEC["layout"]
    for line in text.splitlines():
        if not line.strip():
            continue
        if lay == "json":
            o = json.loads(line)
            out.append({"ts": _ts(o["@timestamp"]), "level": LEVEL[o["severity"]], "message": o["body"]["text"],
                        "request_id": (o.get("trace") or {}).get("id")})
        elif lay == "kv":
            m = re.match(r'ts="([^"]*)" level=(\S+) msg="((?:[^"\\]|\\.)*)"(?: rid=(\S+))?$', line)
            msg = re.sub(r"\\(.)", lambda k: {"n": "\n"}.get(k.group(1), k.group(1)), m.group(3))
            out.append({"ts": _ts(m.group(1)), "level": LEVEL[m.group(2)], "message": msg, "request_id": m.group(4)})
        elif lay == "csv":
            m = re.match(r'(.*?),(\w+),"((?:[^"]|"")*)",(\S*)$', line)
            out.append({"ts": _ts(m.group(1)), "level": LEVEL[m.group(2)], "message": m.group(3).replace('""', '"'),
                        "request_id": m.group(4) or None})
        elif line.startswith("    ") and out:
            out[-1]["message"] += "\n" + line[4:]
        elif lay == "bracket":
            m = re.match(rf"({TS_RE}) \[(\w+)\] (\S+) (.*)$", line)
            rid = m.group(3)[4:] if m.group(3).startswith("req=") else None
            out.append({"ts": _ts(m.group(1)), "level": LEVEL[m.group(2)], "message": m.group(4), "request_id": rid})
        else:
            m = re.match(rf"({TS_RE})\|(\w+)\|(\w*)\|(.*)$", line)
            out.append({"ts": _ts(m.group(1)), "level": LEVEL[m.group(2)], "message": m.group(4),
                        "request_id": m.group(3) or None})
    return out
'''


def solve(seed, workspace):
    for name, info in generate(seed)["formats"].items():
        write(Path(workspace) / "parsers", f"{name}.py", ORACLE.replace("__SPEC__", repr(info["spec"])))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [f["unit_chars"] for f in t["formats"].values()],
            "judgement_turns": 6, "orchestration_turns": 10, "shared_chars": len(SCHEMA_MD)}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# One log schema for every service

We are moving every legacy service's logs onto one schema (`docs/SCHEMA.md`).
For each log format in `samples/`, write `parsers/<format>.py` exposing
`parse(text) -> list[dict]` that turns a whole log file into records in that
schema. Some formats have a note in `docs/formats/`; the rest have only their
sample.

Your parsers will be run on other logs from the same services, not on these
samples, so they must handle the format, not the file.
"""

META = {
    "unit": "log format", "kind": "parser writing", "domain": "log formats", "output_tokens": 2200, "needs_pytest": False,
    "failure_mode": "inferring a format from samples and normalising it exactly; graded on held-out logs",
    "deliverable": "`parsers/<format>.py` with `parse(text) -> list[dict]` for each of 32 formats",
    "grading": "Per format: the fraction of held-out records returned exactly (UTC timestamp to the "
               "millisecond, canonical level, unescaped message with continuation lines, request id or null). "
               "Reward is the mean.",
    "per_unit": "work out the timestamp style and offset, the level encoding, the layout and its escaping, "
                "and any continuation lines -- from a note if there is one, from the sample if not -- then "
                "write and check a parser",
    "traps": [
        "**Offsets.** ISO-with-offset and CLF timestamps are local; the schema wants UTC.",
        "**Level synonyms.** `warning`/`fatal`, single letters, and Python's numeric levels.",
        "**Escaping.** key=value messages escape quotes and newlines; CSV doubles quotes.",
        "**Continuation lines** belong to the previous record's message.",
        "**Held-out grading.** A parser tuned to quirks of the sample, or one that hardcodes it, fails.",
        "**Half the formats are undocumented.**",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
