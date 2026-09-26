#!/usr/bin/env python3
"""LH3 -- reconstruct an incident's causal timeline from 24 hosts' logs.

The on-call ticket (the brief) says db-primary crashed first and took the fleet
down. It did crash -- at the END of the chain. The real first failure is a
certificate reload with a truncated chain on one edge load balancer, eleven
minutes earlier than anything on the database.

What makes it long-horizon: ~35k tokens of logs per host, six log formats, and
per-host clock error. Several hosts' clocks are skewed (stated in each host's
chrony.log) and the queue hosts log in local time (stated in host.yaml), so
ordering events by the raw timestamps picks the wrong root cause -- by design.
Every host has to be read and normalised on its own terms, including the ones
where nothing causal happened, before the fleet-wide order can be trusted.

Carried over from HANDOFF: a poisoned premise in the brief (F2), decoys that
look causal but are not (F4), and the deliverable is a merge of per-host
findings the orchestrator cannot re-derive without re-reading everything.

    python3 lh3_incident_timeline.py --seed 1 --out /fixture
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, write, write_json  # noqa: E402

DAY = datetime(2026, 9, 14, tzinfo=timezone.utc)
WINDOW = (DAY.replace(hour=1, minute=30), DAY.replace(hour=2, minute=40))
CDT = timezone(timedelta(hours=-5))

HOSTS = (["edge-lb-1", "edge-lb-2", "edge-lb-3"] + [f"api-{i}" for i in range(1, 7)]
         + [f"worker-{i}" for i in range(1, 6)] + ["cache-1", "cache-2", "cache-3",
         "queue-1", "queue-2", "db-primary", "db-replica-1", "db-replica-2", "cron-1", "auth-1"])
FAMILY = {"edge": "nginx", "api": "json", "worker": "logfmt", "cache": "redis",
          "queue": "syslog", "db": "postgres", "cron": "syslog", "auth": "json"}

KINDS = ["cert_reload", "tls_handshake_failure", "retry_storm", "queue_backlog", "worker_oom",
         "cache_eviction_storm", "cache_miss_fallback", "db_connection_saturation",
         "db_failover", "replica_promoted",
         # Present in the vocabulary so a wrong answer can be expressed.
         "db_autovacuum_warning", "cron_job_failure", "signing_key_rotation", "deploy",
         "config_change"]

# The causal chain, in true UTC, as offsets from 02:00:00. For kinds that show up
# on several hosts, `spread` lists (host, seconds after the first) -- the
# timeline wants the FIRST occurrence, which is only findable after skew.
CHAIN = [
    ("cert_reload", "edge-lb-2", 9 * 60 + 12, []),
    ("tls_handshake_failure", "edge-lb-2", 9 * 60 + 20, []),
    ("retry_storm", "api-3", 9 * 60 + 41, [("api-6", 20), ("api-1", 12), ("api-2", 33),
                                             ("api-4", 38), ("api-5", 27)]),
    ("queue_backlog", "queue-1", 10 * 60 + 35, [("queue-2", 25)]),
    ("worker_oom", "worker-4", 11 * 60 + 50, [("worker-2", 40)]),
    ("cache_eviction_storm", "cache-2", 12 * 60 + 30, [("cache-1", 15)]),
    ("cache_miss_fallback", "api-5", 13 * 60 + 5, [("api-2", 8)]),
    ("db_connection_saturation", "db-primary", 14 * 60 + 3, []),
    ("db_failover", "db-primary", 14 * 60 + 40, []),
    ("replica_promoted", "db-replica-1", 15 * 60 + 10, []),
]
DECOYS = [
    ("db_autovacuum_warning", "db-primary", 3 * 60 + 30),
    ("cron_job_failure", "cron-1", 8 * 60),
    ("signing_key_rotation", "auth-1", 10 * 60 + 5),
    ("cert_reload", "edge-lb-1", -15 * 60),  # a healthy reload, well before
]
# Chosen so that ordering by RAW timestamps is wrong in exactly the ways that
# matter: api-6 looks like the first retry storm, and it looks earlier than the
# certificate reload -- so a skew-blind reader names api-6 as the root cause.
FIXED_SKEW = {"edge-lb-2": 41.5, "api-3": 55.0, "api-6": -40.0, "db-primary": -95.0,
              "worker-4": 18.0, "cache-2": -22.0}
LOCAL_TIME_HOSTS = {"queue-1", "queue-2"}
TOLERANCE_S = 6


def family(host):
    return FAMILY[host.split("-")[0]]


def at(seconds):
    return DAY.replace(hour=2) + timedelta(seconds=seconds)


# ------------------------------------------------------------------ formatting

def render(fam, host, raw, level, msg, pid, fields=None):
    fields = fields or {}
    if fam == "nginx":
        return f"{raw:%Y/%m/%d %H:%M:%S} [{level.lower()}] {pid}#0: {msg}"
    if fam == "json":
        return json.dumps({"ts": raw.strftime("%Y-%m-%dT%H:%M:%S.") + f"{raw.microsecond // 1000:03d}Z",
                           "level": level.lower(), "host": host, "msg": msg, **fields})
    if fam == "logfmt":
        extra = "".join(f" {k}={v}" for k, v in fields.items())
        return (f"time={raw:%Y-%m-%dT%H:%M:%S}.{raw.microsecond // 1000:03d}Z level={level.lower()} "
                f'msg="{msg}"{extra}')
    if fam == "redis":
        sym = {"INFO": "*", "WARN": "#", "ERROR": "#"}.get(level, "*")
        return f"{pid}:M {raw:%d %b %Y %H:%M:%S}.{raw.microsecond // 1000:03d} {sym} {msg}"
    if fam == "syslog":
        proc = "broker" if host.startswith("queue") else "crond"
        return f"{raw:%b %d %H:%M:%S} {host} {proc}[{pid}]: {level}: {msg}"
    if fam == "postgres":
        return f"{raw:%Y-%m-%d %H:%M:%S}.{raw.microsecond // 1000:03d} UTC [{pid}] {level}:  {msg}"
    raise ValueError(fam)


NOISE = {
    "nginx": [("INFO", "upstream keepalive pool resized to {n}"),
              ("INFO", "{n} active connections, {m} waiting"),
              ("WARN", "client closed connection while waiting for request, client: 10.0.{n}.{m}"),
              ("ERROR", "SSL_do_handshake() failed (SSL: error:0A000126) while SSL handshaking, client: 10.9.{n}.{m}"),
              ("INFO", "health check /healthz ok in {n}ms")],
    "json": [("INFO", "request served", {"route": "/v1/{w}", "status": 200, "ms": "{n}"}),
             ("INFO", "request served", {"route": "/v1/{w}/{m}", "status": 200, "ms": "{n}"}),
             ("WARN", "slow request", {"route": "/v1/{w}", "ms": "{n}0"}),
             ("ERROR", "request failed", {"route": "/v1/{w}", "status": 502, "retries_per_s": "{s}"}),
             ("INFO", "gc pause", {"ms": "{s}"}),
             ("INFO", "upstream stats", {"retries_per_s": "{s}", "cache_hit_ratio": "0.9{m}"})],
    "logfmt": [("INFO", "job done", {"queue": "{w}", "ms": "{n}"}),
               ("INFO", "heap", {"rss_mb": "5{n}", "limit_mb": 2048}),
               ("WARN", "job retried", {"queue": "{w}", "attempt": "{s}"}),
               ("ERROR", "job failed permanently", {"queue": "{w}", "err": "ValidationError"})],
    "redis": [("INFO", "{n} changes in 60 seconds. Saving..."),
              ("INFO", "Background saving terminated with success"),
              ("INFO", "DB saved on disk"),
              ("WARN", "Client id={n} addr=10.2.{m}.{s} closed for idle timeout"),
              ("INFO", "used_memory={n}M maxmemory=4096M evicted_keys={s}")],
    "syslog": [("INFO", "queue {w} depth={n} consumers={s}"),
               ("INFO", "channel opened by 10.3.{m}.{s}"),
               ("WARN", "consumer on {w} slow to ack ({n}ms)"),
               ("ERROR", "connection reset by peer 10.3.{m}.{s}")],
    "postgres": [("LOG", "checkpoint complete: wrote {n} buffers ({s}.{m}%)"),
                 ("LOG", "connection received: host=10.4.{m}.{s} port={n}"),
                 ("LOG", "duration: {n}.{m} ms  statement: SELECT * FROM {w} WHERE id = ${s}"),
                 ("WARNING", "there is already a transaction in progress"),
                 ("ERROR", "duplicate key value violates unique constraint \"{w}_pkey\"")],
}
WORDS = ["orders", "carts", "users", "sessions", "catalog", "prices", "inventory", "search"]


def noise_line(rng, fam, host, raw, pid):
    tpl = rng.choice(NOISE[fam])
    vals = {"n": rng.randint(2, 999), "m": rng.randint(0, 9), "s": rng.randint(1, 9),
            "w": rng.choice(WORDS)}
    level, msg = tpl[0], tpl[1].format(**vals)
    fields = {k: (v.format(**vals) if isinstance(v, str) else v) for k, v in (tpl[2] if len(tpl) > 2 else {}).items()}
    return render(fam, host, raw, level, msg, pid, fields)


# Event lines, per kind, in the vocabulary of the host that emits them. Onset
# kinds also emit a sustained tail -- the onset is where the rate changes.
def event_lines(kind, fam, host, rng):
    """[(seconds_after_event, level, msg, fields)]"""
    if kind == "cert_reload":
        return [(0, "INFO", "reloading certificate bundle /etc/ssl/edge.pem"),
                (1, "WARN", "certificate chain for *.shop.internal has 1 of 3 certificates; "
                            "intermediate CA not found in bundle")]
    if kind == "cert_reload_ok":
        return [(0, "INFO", "reloading certificate bundle /etc/ssl/edge.pem"),
                (1, "INFO", "certificate chain for *.shop.internal verified (3 of 3)")]
    if kind == "tls_handshake_failure":
        return [(t, "ERROR", f"SSL_do_handshake() failed (SSL: error:0A000086 certificate verify failed) "
                             f"while SSL handshaking to upstream, client: 10.9.{rng.randint(0, 9)}.{rng.randint(1, 250)}")
                for t in range(0, 600, 2)]
    if kind == "retry_storm":
        return [(t, "WARN", "upstream retry budget exhausted",
                 {"retries_per_s": rng.randint(600, 900), "upstream": "edge"}) for t in range(0, 300, 5)]
    if kind == "queue_backlog":
        return [(t, "WARN", f"queue orders depth={20000 + 900 * t} exceeds high watermark 20000") for t in range(0, 240, 6)]
    if kind == "worker_oom":
        return [(-3, "WARN", "heap", {"rss_mb": 2011, "limit_mb": 2048}),
                (0, "ERROR", "process killed by OOM killer", {"rss_mb": 2049, "limit_mb": 2048}),
                (2, "INFO", "supervisor restarting worker", {"reason": "oom"})]
    if kind == "cache_eviction_storm":
        return [(t, "WARN", f"maxmemory reached; evicted_keys={40000 + 3000 * t} in last second") for t in range(0, 180, 3)]
    if kind == "cache_miss_fallback":
        return [(t, "WARN", "cache miss; falling back to primary database",
                 {"miss_ratio": round(0.6 + rng.random() * 0.3, 2)}) for t in range(0, 180, 4)]
    if kind == "db_connection_saturation":
        return [(t, "FATAL", "sorry, too many clients already") for t in range(0, 36, 2)]
    if kind == "db_failover":
        return [(0, "PANIC", "could not write to file \"pg_wal/xlogtemp.4411\": No space left on device"),
                (1, "LOG", "server process (PID 4411) was terminated by signal 6: Aborted"),
                (2, "LOG", "terminating any other active server processes")]
    if kind == "replica_promoted":
        return [(0, "LOG", "received promote request"),
                (1, "LOG", "selected new timeline ID: 7"),
                (2, "LOG", "database system is ready to accept connections")]
    if kind == "db_autovacuum_warning":
        return [(0, "WARNING", "oldest xmin is far in the past; autovacuum of table \"orders\" "
                               "may be delayed")]
    if kind == "cron_job_failure":
        return [(0, "ERROR", "job nightly-report exited with status 1 (report bucket missing)")]
    if kind == "signing_key_rotation":
        return [(0, "INFO", "rotating token signing key", {"kid": "k-2026-09-14"}),
                (1, "INFO", "new signing key active; previous key valid for 24h", {"kid": "k-2026-09-14"})]
    raise ValueError(kind)


# ----------------------------------------------------------------------- layout

def plan(seed):
    rng = rng_for(seed, "plan")
    hosts = {}
    for h in HOSTS:
        skew = FIXED_SKEW.get(h, round(rng.uniform(-15, 15), 3))
        hosts[h] = {"skew_s": skew, "local_time": h in LOCAL_TIME_HOSTS, "events": []}
    truth_events = []
    for kind, host, t, spread in CHAIN:
        truth_events.append({"host": host, "kind": kind, "utc": at(t)})
        hosts[host]["events"].append((kind, at(t)))
        for other, delta in spread:
            hosts[other]["events"].append((kind, at(t + delta)))
    for kind, host, t in DECOYS:
        hosts[host]["events"].append(("cert_reload_ok" if t < 0 else kind, at(t)))
    return hosts, truth_events


def raw_time(true_utc, host_info):
    raw = true_utc + timedelta(seconds=host_info["skew_s"])
    return raw.astimezone(CDT) if host_info["local_time"] else raw


def generate(seed, out=None, lines_per_host=1150):
    hosts, truth_events = plan(seed)
    files = {}
    for h, info in hosts.items():
        rng = rng_for(seed, "host", h)
        fam = family(h)
        pid = rng.randint(1000, 65000)
        entries = []
        span = (WINDOW[1] - WINDOW[0]).total_seconds()
        for _ in range(lines_per_host):
            true = WINDOW[0] + timedelta(seconds=rng.uniform(0, span))
            entries.append((true, noise_line(rng, fam, h, raw_time(true, info), pid)))
        for kind, when in info["events"]:
            for spec in event_lines(kind, fam, h, rng):
                dt, level, msg = spec[0], spec[1], spec[2]
                fields = spec[3] if len(spec) > 3 else {}
                true = when + timedelta(seconds=dt, milliseconds=rng.randint(0, 900))
                entries.append((true, render(fam, h, raw_time(true, info), level, msg, pid, fields)))
        entries.sort(key=lambda e: e[0])
        base = f"incident/hosts/{h}"
        files[f"{base}/app.log"] = "\n".join(line for _, line in entries) + "\n"
        files[f"{base}/host.yaml"] = (
            f"host: {h}\nrole: {h.rsplit('-', 1)[0]}\nlog_format: {fam}\n"
            f"log_timezone: {'America/Chicago (CDT, UTC-5)' if info['local_time'] else 'UTC'}\n")
        chrony = []
        for hour in (0, 1, 2, 3):
            drift = rng.uniform(-0.4, 0.4)
            chrony.append(f"2026-09-14T{hour:02d}:00:00 reference=ntp1.internal "
                          f"offset={info['skew_s'] + drift:+.3f}s "
                          f"(positive: this host's clock was AHEAD of reference)")
        files[f"{base}/chrony.log"] = "\n".join(chrony) + "\n"

    files["incident/README.md"] = README
    truth = {
        "seed": seed,
        "premise_correct": False,
        "root_cause": {"host": CHAIN[0][1], "kind": CHAIN[0][0]},
        "events": [{**e, "utc": e["utc"].strftime("%Y-%m-%dT%H:%M:%SZ")} for e in truth_events],
        "unit_chars": {h: sum(len(v) for k, v in files.items() if k.startswith(f"incident/hosts/{h}/"))
                       for h in HOSTS},
    }
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


README = """# Incident INC-2317 -- 2026-09-14, checkout outage

Logs from every host in the checkout fleet, 01:30-02:40 UTC.

- `hosts/<host>/app.log` -- the host's main log, in its own format.
- `hosts/<host>/host.yaml` -- role, log format, and the timezone the log is written in.
- `hosts/<host>/chrony.log` -- clock-offset measurements against the reference NTP
  server. A positive offset means that host's clock was AHEAD of true time, so
  its timestamps must be moved back by that much.

Log timestamps are the host's own clock. They are not comparable across hosts
until each is corrected for its offset and timezone.
"""


# ------------------------------------------------------------------------ grade

def _parse_utc(s):
    return datetime.strptime(s.replace("+00:00", "Z").rstrip("Z")[:19], "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=timezone.utc)


def grade(seed, answer):
    """0.1 premise flagged, 0.3 root cause, 0.4 event recall, 0.1 pairwise order
    of recalled events, 0.1 precision. `answer` is the parsed timeline.json."""
    truth = generate(seed)
    result = {"premise": answer.get("premise_correct") is False}
    rc = answer.get("root_cause") or {}
    result["root_cause"] = (rc.get("host"), rc.get("kind")) == (truth["root_cause"]["host"],
                                                               truth["root_cause"]["kind"])
    submitted = []
    for e in answer.get("events") or []:
        try:
            submitted.append((e["host"], e["kind"], _parse_utc(e["utc"])))
        except (KeyError, ValueError, TypeError, AttributeError):
            continue
    matched, used = [], set()
    for i, t in enumerate(truth["events"]):
        tu = _parse_utc(t["utc"])
        for j, (h, k, u) in enumerate(submitted):
            if j not in used and (h, k) == (t["host"], t["kind"]) and abs((u - tu).total_seconds()) <= TOLERANCE_S:
                matched.append((i, j))
                used.add(j)
                break
    n = len(truth["events"])
    recall = len(matched) / n
    pairs = [(a, b) for a in matched for b in matched if a[0] < b[0]]
    order = (sum(1 for a, b in pairs if submitted[a[1]][2] <= submitted[b[1]][2]) / len(pairs)) if pairs else 0.0
    precision = len(matched) / len(submitted) if submitted else 0.0
    result.update({"recall": round(recall, 3), "order": round(order, 3),
                   "precision": round(precision, 3),
                   "missed": [truth["events"][i]["kind"] for i in range(n) if i not in {m[0] for m in matched}]})
    result["reward"] = round(0.1 * result["premise"] + 0.3 * result["root_cause"]
                             + 0.4 * recall + 0.1 * order + 0.1 * precision, 4)
    return result


def oracle_answer(seed):
    truth = generate(seed)
    return {"premise_correct": False, "root_cause": truth["root_cause"], "events": truth["events"]}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out")
    ap.add_argument("--answers")
    ap.add_argument("--grade", help="timeline.json to grade; prints JSON")
    ap.add_argument("--solve", help="write the reference timeline.json here")
    args = ap.parse_args(argv)
    if args.grade:
        try:
            answer = json.loads(Path(args.grade).read_text())
        except (OSError, ValueError):
            answer = {}
        print(json.dumps(grade(args.seed, answer if isinstance(answer, dict) else {}), indent=2))
        return
    if args.solve:
        write_json(Path(args.solve).parent, Path(args.solve).name, oracle_answer(args.seed))
        return
    truth = generate(args.seed, args.out)
    if args.answers:
        Path(args.answers).write_text(json.dumps(truth, indent=2) + "\n")


if __name__ == "__main__":
    main()
