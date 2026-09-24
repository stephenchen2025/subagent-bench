"""P -- parallel probes. K independent investigations, each three dependent hops.

K services are degraded. For each one the agent must:

1. `svcctl status <svc>` -- a health dump whose incident notes describe the
   failing part of the service *by what it does*, never by name;
2. `svcctl components <svc>` -- match that description to a component name
   (the descriptions are paraphrases, and neighbouring components share words);
3. `svcctl logs <svc> <component>` -- read the logs to name the root cause from a
   fixed menu. Logs carry resolved, historical incidents of *other* causes, so the
   first alarming line is not the answer.

Every call has latency (`SVCCTL_LATENCY`, default 2s), and each hop depends on
reading the last. Items are independent of each other, which is exactly the
shape Anthropic reports parallel subagents cutting wall-clock time on. A solo
agent can batch hop 1 across services in one command; the per-observation cap
makes that lossy as K grows, but it remains a legitimate strategy, and a strong
solo baseline is the point.

The data lives in an encoded blob beside the tool so reading it directly is no
cheaper than calling the tool. Ground truth is never in the image.
"""

import base64
import json
import zlib

from orch.task import DELEGATE, OrchTask, rng_for, task_id

FAMILY = "P"
SIZES = (15, 25, 38)
SERVICES_PER_WORKER = 3

SERVICE_NAMES = [
    "ledger", "notifier", "authz", "search-indexer", "billing-sync", "media-resizer",
    "geo-lookup", "invoice-render", "session-store", "rate-limiter", "feed-builder",
    "export-worker", "catalog-api", "webhook-relay", "audit-trail", "quota-keeper",
    "thumbnailer", "payout-batch", "email-digest", "fraud-score",
    "tax-calc", "sso-bridge", "cart-merge", "promo-engine", "inventory-sync",
    "label-printer", "returns-desk", "shipment-tracker", "review-moderator",
    "loyalty-points", "price-watch", "consent-log", "backup-rotator", "cdn-purger",
    "ledger-archiver", "pdf-stamper", "sms-gateway", "chat-router", "survey-collector",
    "dns-updater", "key-vault", "job-reaper", "cost-reporter", "schema-registry",
]

# Each component: (name, catalogue description, incident-notes paraphrase).
COMPONENTS = [
    ("token-refresher", "renews short-lived upstream credentials before they lapse",
     "the part that keeps upstream credentials fresh"),
    ("blob-writer", "persists uploaded payloads to local scratch disk",
     "whatever stores incoming payloads on the box itself"),
    ("peer-resolver", "maps peer service names to addresses at startup and on retry",
     "the piece responsible for finding where peer services live"),
    ("config-loader", "parses the service's INI settings and hot-reloads them",
     "the bit that reads and reloads the settings file"),
    ("batch-assembler", "accumulates records in memory until a batch is full",
     "the stage that buffers records in RAM before flushing"),
    ("http-frontend", "terminates inbound HTTP and routes requests",
     "the layer that accepts incoming web requests"),
    ("metrics-shipper", "forwards counters and timings to the metrics backend",
     "the reporter that sends telemetry out"),
    ("cache-warmer", "preloads hot keys into the in-process cache after deploys",
     "the job that pre-fills the cache after a release"),
    ("queue-consumer", "pulls work items off the shared job queue",
     "the worker loop that takes jobs off the queue"),
    ("schema-migrator", "applies pending database migrations on boot",
     "the startup step that updates the database schema"),
]

CAUSES = ["expired-credential", "disk-full", "dns-failure", "config-typo", "out-of-memory"]

# Log lines that establish a cause, written without the menu's words.
CAUSE_LINES = {
    "expired-credential": [
        "upstream rejected request: certificate not valid after {date}; presented cert is past its end date",
        "401 from identity provider: signing key id {hexid} is no longer accepted (validity window closed)",
    ],
    "disk-full": [
        "write of chunk {hexid} failed: ENOSPC while flushing to /var/scratch",
        "could not persist payload {hexid}: device has 0 bytes available on /var/scratch",
    ],
    "dns-failure": [
        "lookup of {peer}.internal failed: SERVFAIL from 10.0.0.2:53",
        "no address records returned for {peer}.internal after 3 attempts; giving up",
    ],
    "config-typo": [
        "settings reload rejected: unknown key 'retires' in section [client] (line {line})",
        "failed to parse settings: expected integer for 'timeout_ms', got '30O0' (line {line})",
    ],
    "out-of-memory": [
        "worker pid {pid} terminated by kernel: anon-rss {mb}MB exceeds cgroup limit",
        "allocation of {mb}MB batch buffer failed; process killed by the memory controller",
    ],
}
# Historical, explicitly resolved incidents of other causes: bait for grep.
RESOLVED_TEMPLATES = {
    "expired-credential": "[resolved {date}] credential rotation lag caused a brief 401 burst; rotated and closed",
    "disk-full": "[resolved {date}] scratch volume hit 97% during backfill; cleaned up, ticket closed",
    "dns-failure": "[resolved {date}] resolver flapped during network maintenance; no action needed",
    "config-typo": "[resolved {date}] bad settings push reverted within 4 minutes",
    "out-of-memory": "[resolved {date}] one pod OOM-restarted during load test; limits raised since",
}
# Benign errors on healthy components, so `grep ERROR` over every component's
# logs does not skip the step of matching the incident notes to a component.
BENIGN_ERRORS = [
    "ERROR transient 503 from {peer} on /v1/{route}; retry succeeded",
    "ERROR client closed connection early (dur_ms={n}); request abandoned by caller",
    "ERROR slow consumer detected, backpressure applied for {n}ms; recovered",
]
NOISE_LINES = [
    "request completed status=200 route=/v1/{route} dur_ms={n}",
    "gc pause {n}ms (young gen)",
    "heartbeat ok peer={peer} lag_ms={n}",
    "cache hit ratio {pct}% over last 60s",
    "rotated log file, {n} lines archived",
    "health probe ok from 10.0.{a}.{b}",
    "slow query {n}ms on table events (below alert threshold)",
    "retrying idempotent call to {peer} (attempt 1/3) -- succeeded",
]

MENU = ", ".join(f"`{c}`" for c in CAUSES)

INSTRUCTION = """\
{k} production services are degraded: {services}.

For each service, find the component that is failing and the root cause. Use the
`svcctl` tool:

- `svcctl status <service>`: health and incident notes
- `svcctl components <service>`: the service's components
- `svcctl logs <service> <component>`: recent logs for one component

The root cause is exactly one of: {menu}.

Write the result to `answer.json` in the working directory:

```json
{{"services": {{"<service>": {{"component": "<component>", "cause": "<cause>"}}}}}}
```

Each service is scored separately: half for the component, half for the cause.
"""

WORKER_BRIEF = """\
Diagnose these degraded services: {services}. For each, use `svcctl`:
`svcctl status <service>` (incident notes describe the failing part by what it
does), then `svcctl components <service>` (match that description to a component
name), then `svcctl logs <service> <component>` (find the root cause; ignore
incidents marked resolved).

The root cause is exactly one of: {menu}.

In your report, give one JSON object per service, one per line:
{{"service": "<service>", "component": "<component>", "cause": "<cause>"}}
"""

SVCCTL = r'''#!/usr/bin/env python3
"""svcctl -- service diagnostics (orchestrator-track fixture)."""
import base64, json, os, sys, time, zlib

DB = os.environ.get("SVCCTL_DB", "/opt/svcctl/db")


def load():
    with open(DB) as fh:
        return json.loads(zlib.decompress(base64.b64decode(fh.read())))


def main(argv):
    time.sleep(float(os.environ.get("SVCCTL_LATENCY", "2")))
    db = load()
    if len(argv) >= 1 and argv[0] == "list":
        print("\n".join(sorted(db)))
        return 0
    if len(argv) < 2 or argv[0] not in ("status", "components", "logs"):
        print("usage: svcctl list | status <svc> | components <svc> | logs <svc> <component>")
        return 2
    svc = db.get(argv[1])
    if svc is None:
        print(f"svcctl: unknown service {argv[1]!r}")
        return 1
    if argv[0] == "status":
        print(svc["status"])
    elif argv[0] == "components":
        print(svc["components"])
    else:
        if len(argv) < 3 or argv[2] not in svc["logs"]:
            print(f"svcctl: unknown component for {argv[1]}")
            return 1
        print(svc["logs"][argv[2]])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
'''


def _date(rng):
    return f"2026-{rng.randint(1, 8):02d}-{rng.randint(1, 28):02d}"


def _fill(template, rng, peer):
    return template.format(
        date=_date(rng), hexid=f"{rng.getrandbits(32):08x}", peer=peer,
        line=rng.randint(3, 80), pid=rng.randint(200, 9000), mb=rng.randint(900, 4000),
        route=rng.choice(["items", "users", "orders", "search"]), n=rng.randint(2, 900),
        pct=rng.randint(60, 99), a=rng.randint(0, 9), b=rng.randint(2, 250),
    )


def _status(rng, name, notes_phrase):
    rows = []
    for metric in ("p50_ms", "p99_ms", "error_rate", "rps", "cpu_pct", "mem_pct",
                   "open_conns", "queue_depth", "restarts_24h", "gc_pause_ms"):
        rows.append(f"  {metric:<14}" + "  ".join(f"{rng.randint(1, 999):>5}" for _ in range(8)))
    events = [f"  {_date(rng)}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}Z  "
              f"{rng.choice(['deploy', 'scale-up', 'config push', 'cert check', 'probe', 'page'])} "
              f"{rng.choice(['ok', 'ok', 'ok', 'noted', 'acked'])}" for _ in range(12)]
    return (
        f"service: {name}\nstate: DEGRADED since {_date(rng)}\n"
        f"replicas: {rng.randint(2, 12)} desired, {rng.randint(1, 12)} ready\n\n"
        "metrics (last 8 intervals):\n" + "\n".join(rows) + "\n\nrecent events:\n"
        + "\n".join(events) + "\n\nincident notes (on-call):\n"
        f"  Error volume started climbing at {rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}. "
        f"Traces point at {notes_phrase}. Everything else in the request path looks "
        "healthy. Customer impact: elevated error rate on a subset of calls. "
        "Next step: check that component's logs.\n"
    )


def _components(rng, comps):
    lines = [f"  {c[0]:<18} {c[1]}" for c in comps]
    return "components:\n" + "\n".join(lines) + "\n"


def _logs(rng, cause, peer, is_culprit, other_causes):
    lines = []
    for _ in range(rng.randint(22, 30)):
        lines.append(_fill(rng.choice(NOISE_LINES), rng, peer))
    for other in rng.sample(other_causes, 2):
        lines.insert(rng.randrange(len(lines)), _fill(RESOLVED_TEMPLATES[other], rng, peer))
    if not is_culprit:
        for _ in range(rng.randint(1, 3)):
            lines.insert(rng.randrange(len(lines)), _fill(rng.choice(BENIGN_ERRORS), rng, peer))
    if is_culprit:
        bad = CAUSE_LINES[cause]
        pos = rng.randrange(len(lines) // 2, len(lines))
        for j in range(4):
            lines.insert(pos + j, "ERROR " + _fill(rng.choice(bad), rng, peer))
    stamped = []
    for line in lines:
        prefix = f"{_date(rng)}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}Z"
        level = "" if line.startswith(("ERROR", "[resolved")) else "INFO "
        stamped.append(f"{prefix} {level}{line}")
    return "\n".join(stamped) + "\n"


def generate(size, seed):
    rng = rng_for(FAMILY, size, seed)
    services = rng.sample(SERVICE_NAMES, size)
    db, truth = {}, {}
    for name in services:
        comps = rng.sample(COMPONENTS, rng.randint(6, 8))
        culprit = rng.choice(comps)
        cause = rng.choice(CAUSES)
        peer = rng.choice([s for s in SERVICE_NAMES if s != name])
        others = [c for c in CAUSES if c != cause]
        db[name] = {
            "status": _status(rng, name, culprit[2]),
            "components": _components(rng, comps),
            "logs": {c[0]: _logs(rng, cause, peer, c is culprit, others) for c in comps},
        }
        truth[name] = {"component": culprit[0], "cause": cause}
    blob = base64.b64encode(zlib.compress(json.dumps(db).encode())).decode()
    answer = json.dumps({"services": truth}, indent=2)
    listed = ", ".join(f"`{s}`" for s in services)
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=DELEGATE,
        instruction=INSTRUCTION.format(k=size, services=listed, menu=MENU),
        files={},
        truth={"services": truth},
        solution=f"cat > answer.json <<'EOF'\n{answer}\nEOF\n",
        work_items=list(services),
        oracle_plan=_plan(services),
        tool_files={"/opt/svcctl/svcctl": SVCCTL, "/opt/svcctl/db": blob},
        env={"SVCCTL_LATENCY": "2"},
    )


def _plan(services):
    groups = [services[i:i + SERVICES_PER_WORKER]
              for i in range(0, len(services), SERVICES_PER_WORKER)]
    return [
        {"items": g, "brief": WORKER_BRIEF.format(services=", ".join(g), menu=MENU)}
        for g in groups
    ]


def merge_reports(reports):
    found = {}
    for report in reports:
        for line in (report or "").splitlines():
            line = line.strip().strip(",")
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and {"service", "component", "cause"} <= set(obj):
                found[obj["service"]] = {"component": obj["component"], "cause": obj["cause"]}
    return {"services": found}


def decode_db(blob):
    return json.loads(zlib.decompress(base64.b64decode(blob)))
