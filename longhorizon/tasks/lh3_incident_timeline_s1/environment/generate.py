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

# The causal chain's SHAPE is fixed; which hosts carry it, when it starts, and
# the clock skews are drawn per seed (see scenario()). For kinds that show up on
# several hosts, the timeline wants the FIRST occurrence in true UTC, which is
# only findable after every candidate host is corrected for skew.
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

def scenario(seed):
    """Draw this seed's incident: (chain, decoys, fixed_skews).

    The skews are not random noise. They are solved for, so that ordering by
    RAW timestamps is wrong in the ways that matter: a decoy api host's retry
    storm reads as earlier than the certificate reload, and db-primary's events
    read as earlier than they were.
    """
    rng = rng_for(seed, "scenario")
    edges = ["edge-lb-1", "edge-lb-2", "edge-lb-3"]
    apis = [f"api-{i}" for i in range(1, 7)]
    bad_edge = rng.choice(edges)
    healthy_edge = rng.choice([e for e in edges if e != bad_edge])
    rng.shuffle(apis)
    first_api, decoy_api, *other_apis = apis
    queues = rng.sample(["queue-1", "queue-2"], 2)
    workers = rng.sample([f"worker-{i}" for i in range(1, 6)], 2)
    caches = rng.sample(["cache-1", "cache-2", "cache-3"], 2)
    miss_apis = rng.sample(apis, 2)
    replica = rng.choice(["db-replica-1", "db-replica-2"])

    base = rng.randint(8 * 60, 10 * 60)            # cert reload, seconds after 02:00
    decoy_delta = rng.randint(15, 25)              # decoy api host lags the first by this
    t = {"cert": base, "tls": base + 8, "retry": base + 29,
         "queue": base + rng.randint(80, 100), "oom": base + rng.randint(150, 170),
         "evict": base + rng.randint(190, 210), "miss": base + rng.randint(225, 240),
         "sat": base + rng.randint(290, 305), "fail": base + rng.randint(325, 340)}
    t["promote"] = t["fail"] + rng.randint(25, 35)

    chain = [
        ("cert_reload", bad_edge, t["cert"], []),
        ("tls_handshake_failure", bad_edge, t["tls"], []),
        ("retry_storm", first_api, t["retry"],
         [(decoy_api, decoy_delta)] + [(h, rng.randint(8, 40)) for h in other_apis]),
        ("queue_backlog", queues[0], t["queue"], [(queues[1], rng.randint(15, 30))]),
        ("worker_oom", workers[0], t["oom"], [(workers[1], rng.randint(30, 50))]),
        ("cache_eviction_storm", caches[0], t["evict"], [(caches[1], rng.randint(10, 20))]),
        ("cache_miss_fallback", miss_apis[0], t["miss"], [(miss_apis[1], rng.randint(6, 12))]),
        ("db_connection_saturation", "db-primary", t["sat"], []),
        ("db_failover", "db-primary", t["fail"], []),
        ("replica_promoted", replica, t["promote"], []),
    ]
    decoys = [
        ("db_autovacuum_warning", "db-primary", base - rng.randint(300, 420)),
        ("cron_job_failure", "cron-1", base - rng.randint(30, 90)),
        ("signing_key_rotation", "auth-1", base + rng.randint(40, 70)),
        ("cert_reload_ok", healthy_edge, base - rng.randint(800, 1000)),
    ]
    edge_skew = round(rng.uniform(35, 50), 1)
    skews = {
        bad_edge: edge_skew,
        # Ahead of true time: the real first retry storm reads as late.
        first_api: round(rng.uniform(45, 60), 1),
        # Behind, by enough that its storm reads as earlier than the cert reload.
        decoy_api: round(edge_skew - 29 - decoy_delta - rng.uniform(8, 15), 1),
        "db-primary": round(-rng.uniform(80, 100), 1),
        workers[0]: round(rng.uniform(10, 25), 1),
        caches[0]: round(-rng.uniform(15, 30), 1),
    }
    return chain, decoys, skews


def plan(seed):
    rng = rng_for(seed, "plan")
    chain, decoys, fixed_skew = scenario(seed)
    hosts = {}
    for h in HOSTS:
        skew = fixed_skew.get(h, round(rng.uniform(-15, 15), 3))
        hosts[h] = {"skew_s": skew, "local_time": h in LOCAL_TIME_HOSTS, "events": []}
    truth_events = []
    for kind, host, t, spread in chain:
        truth_events.append({"host": host, "kind": kind, "utc": at(t)})
        hosts[host]["events"].append((kind, at(t)))
        for other, delta in spread:
            hosts[other]["events"].append((kind, at(t + delta)))
    for kind, host, t in decoys:
        hosts[host]["events"].append((kind, at(t)))
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
        "root_cause": {"host": truth_events[0]["host"], "kind": truth_events[0]["kind"]},
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


def shape(seed):
    t = generate(seed)
    return {"unit_chars": list(t["unit_chars"].values()),
            "judgement_turns": 4, "orchestration_turns": 15, "shared_chars": len(README)}


def oracle(seed):
    return oracle_answer(seed)


ANSWER_PATH = "/workspace/answer/timeline.json"
INSTRUCTION = """\
# INC-2317: build the timeline

From the on-call ticket:

> db-primary crashed at about 02:14 UTC and took checkout down with it. Confirm
> that db-primary was the first failure, and build the incident timeline for the
> postmortem.

Everything we have is in `/workspace/incident/`, with one directory per host.
Start with `incident/README.md`.

Write `/workspace/answer/timeline.json`:

```json
{
  "premise_correct": false,
  "root_cause": {"host": "...", "kind": "..."},
  "events": [
    {"host": "...", "kind": "...", "utc": "2026-09-14T02:09:12Z"}
  ]
}
```

- `premise_correct`: was db-primary really the first failure?
- `events`: the incident's causal chain, in order. Give one entry per kind, at
  that kind's first occurrence anywhere in the fleet, with the timestamp in
  true UTC (corrected for that host's clock). List only events that are part of
  this incident.
- `kind` must be one of: __KINDS__.
""".replace("__KINDS__", ", ".join(f"`{k}`" for k in KINDS))


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
