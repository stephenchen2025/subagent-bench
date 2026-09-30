#!/usr/bin/env python3
"""LH18 -- bring 48 Dockerfiles into line with the container policy.

services/<svc>/Dockerfile for 48 services; docs/CONTAINER_POLICY.md has six
rules and docs/APPROVED_BASES.md the only base images allowed, with digests:

- R1 base images pinned to the approved digest for their tag -- and a
  deprecated tag replaced by its listed successor;
- R2 the final stage runs as a non-root user;
- R3 no secret VALUES in ENV or ARG (secrets arrive via
  `RUN --mount=type=secret`). What counts as a secret is defined by the value,
  not the name: `ENV SECRET_ROTATION_DAYS=30` is fine, `ENV GH=ghp_...` is not;
- R4 nothing piped from the network into a shell (`curl ... | sh`); install the
  tool from the package listed in the policy instead;
- R5 a service that EXPOSEs a port has a HEALTHCHECK against its own health
  endpoint, whose port and path are in that service's README (they differ);
- R6 apt installs use --no-install-recommends and clean /var/lib/apt/lists in
  the same RUN.

Behaviour must not change: every COPY, CMD, ENTRYPOINT, EXPOSE and WORKDIR
line the service had must still be there. The grader parses each Dockerfile
and checks every rule that applies, plus that preservation.

    python3 lh18_docker_hardening.py --seed 1 --out /fixture
"""

import hashlib
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import load_json_answer, rng_for, standard_main, write  # noqa: E402

N_SERVICES = 48
BASES = {"python:3.12-slim": None, "node:22-alpine": None, "golang:1.23": None,
         "debian:bookworm-slim": None, "eclipse-temurin:21-jre": None}
DEPRECATED = {"python:3.10-slim": "python:3.12-slim", "node:18-alpine": "node:22-alpine",
              "debian:buster-slim": "debian:bookworm-slim", "openjdk:17-jre": "eclipse-temurin:21-jre"}
TOOLS = {"poetry": "python3-poetry", "yq": "yq", "helm": "helm", "just": "just"}
SECRET_VALUES = ["ghp_{h36}", "AKIA{u16}", "xoxb-{d12}-{h24}", "sk_live_{h24}"]
HARMLESS_ENV = [("SECRET_ROTATION_DAYS", "30"), ("TOKEN_TTL_SECONDS", "900"), ("API_KEY_HEADER", "X-Api-Key"),
                ("PASSWORD_MIN_LENGTH", "12")]


def digest(tag):
    return "sha256:" + hashlib.sha256(tag.encode()).hexdigest()


def _secret(rng):
    tpl = rng.choice(SECRET_VALUES)
    hexs = lambda n: "".join(rng.choice("0123456789abcdef") for _ in range(n))  # noqa: E731
    return (tpl.replace("{h36}", hexs(36)).replace("{u16}", "".join(rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ234567") for _ in range(16)))
            .replace("{d12}", "".join(rng.choice("0123456789") for _ in range(12))).replace("{h24}", hexs(24)))


SECRET_RE = re.compile(r"(ghp_[0-9a-f]{36}|AKIA[A-Z2-7]{16}|xoxb-\d{12}-[0-9a-f]{24}|sk_live_[0-9a-f]{24})")


def build(rng, name):
    """Return (dockerfile, readme, facts) for one service, with a random set of violations."""
    stack = rng.choice(["python", "node", "go", "java"])
    port = rng.choice([8000, 8080, 3000, 9090, 5000])
    health = rng.choice(["/healthz", "/health", "/-/ready", "/status/live"])
    exposes = rng.random() < 0.8
    v = set(rng.sample(["R1", "R2", "R3", "R4", "R6"], rng.randint(2, 4)))
    if stack == "python":
        base = "python:3.10-slim" if rng.random() < 0.5 else "python:3.12-slim"
        build_base = None
        body = ["WORKDIR /app", "COPY requirements.txt .", "RUN pip install --no-cache-dir -r requirements.txt",
                "COPY src/ ./src/"]
        cmd = f'CMD ["python", "-m", "src.main", "--port", "{port}"]'
    elif stack == "node":
        base = "node:18-alpine" if rng.random() < 0.5 else "node:22-alpine"
        build_base = None
        body = ["WORKDIR /app", "COPY package.json package-lock.json ./", "RUN npm ci --omit=dev", "COPY . ."]
        cmd = f'CMD ["node", "server.js", "--port={port}"]'
    elif stack == "go":
        build_base = "golang:1.23"
        base = "debian:buster-slim" if rng.random() < 0.5 else "debian:bookworm-slim"
        body = ["WORKDIR /srv", "COPY --from=build /out/app /srv/app"]
        cmd = f'ENTRYPOINT ["/srv/app", "-listen=:{port}"]'
    else:
        build_base = None
        base = "openjdk:17-jre" if rng.random() < 0.5 else "eclipse-temurin:21-jre"
        body = ["WORKDIR /opt/app", "COPY target/app.jar app.jar"]
        cmd = f'ENTRYPOINT ["java", "-jar", "app.jar", "--server.port={port}"]'
    if "R1" not in v and base in DEPRECATED:
        v.add("R1")
    lines = []
    if build_base:
        lines += [f"FROM {build_base} AS build" if "R1" in v else f"FROM {build_base}@{digest(build_base)} AS build",
                  "WORKDIR /src", "COPY . .", "RUN go build -o /out/app ./cmd/app", ""]
    pinned = f"FROM {base}" if "R1" in v or base in DEPRECATED else f"FROM {base}@{digest(base)}"
    lines.append(pinned)
    harmless = rng.choice(HARMLESS_ENV)
    lines.append(f"ENV {harmless[0]}={harmless[1]}")
    if "R3" in v:
        key = rng.choice(["GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "SLACK_BOT_TOKEN", "STRIPE_KEY"])
        lines.append(f"{rng.choice(['ENV', 'ARG'])} {key}={_secret(rng)}")
    apt_ok = "RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*"
    apt_bad = "RUN apt-get update && apt-get install -y ca-certificates"
    if stack in ("python", "go", "java") or "R6" in v:
        lines.append(apt_bad if "R6" in v else apt_ok)
    tool = rng.choice(list(TOOLS))
    if "R4" in v:
        lines.append(f"RUN curl -sSL https://get.{tool}.example/install.sh | sh")
    lines += body
    if exposes:
        lines.append(f"EXPOSE {port}")
    if "R2" not in v:
        lines += ["RUN useradd --uid 10001 --create-home app" if "alpine" not in base
                  else "RUN adduser -D -u 10001 app", "USER app"]
    elif rng.random() < 0.5:
        lines.append("USER root")
    lines.append(cmd)
    readme = (f"# {name}\n\nStack: {stack}. Listens on port {port}.\n\nHealth endpoint: `GET {health}` on port "
              f"{port} returns 200 when the service is ready.\n")
    facts = {"stack": stack, "port": port, "health": health, "exposes": exposes, "base": base,
             "build_base": build_base, "violations": sorted(v), "tool": tool if "R4" in v else None,
             "keep": [line for line in lines if line.split(" ")[0] in ("COPY", "CMD", "ENTRYPOINT", "EXPOSE", "WORKDIR")]}
    return "\n".join(lines) + "\n", readme, facts


POLICY = f"""# Container policy

Every service's Dockerfile must satisfy all of these. Rules about "the final
stage" apply to the stage after the last `FROM`.

- **R1 Pinned, approved bases.** Every `FROM` names an image from
  `APPROVED_BASES.md` as `image:tag@<digest>`, with that tag's digest.
  Deprecated tags must be replaced by the successor listed there.
- **R2 Non-root.** The final stage ends with a non-root `USER` (not `root`, not 0).
- **R3 No secrets in the image.** No `ENV` or `ARG` may carry a secret value.
  A secret value is one matching a credential format: `ghp_` + 36 hex,
  `AKIA` + 16 base32, `xoxb-` + 12 digits + `-` + 24 hex, `sk_live_` + 24 hex.
  Variables that merely have secret-sounding NAMES are fine. Secrets are
  provided at build time with `RUN --mount=type=secret,id=<name>`.
- **R4 No piping downloads into a shell.** Replace `curl ... | sh` installers
  with the distribution package: {", ".join(f"`{k}` -> `{p}`" for k, p in TOOLS.items())}.
- **R5 Health checks.** If the final stage has an `EXPOSE`, it has a
  `HEALTHCHECK` that requests the service's health endpoint (see its README)
  on the exposed port, e.g. `HEALTHCHECK CMD curl -fsS http://localhost:<port><path> || exit 1`.
- **R6 Lean apt.** `apt-get install` uses `--no-install-recommends`, and the same
  `RUN` removes `/var/lib/apt/lists/*`.

Do not change what the service does: keep every `COPY`, `CMD`, `ENTRYPOINT`,
`EXPOSE` and `WORKDIR` line.
"""


def approved_md():
    rows = [f"| `{t}` | `{digest(t)}` | approved |" for t in BASES]
    rows += [f"| `{t}` | -- | deprecated: use `{s}` |" for t, s in DEPRECATED.items()]
    return "# Approved base images\n\n| image:tag | digest | status |\n|---|---|---|\n" + "\n".join(rows) + "\n"


def generate(seed, out=None):
    rng = rng_for(seed, "plan")
    words = ["billing", "search", "gateway", "ledger", "media", "notify", "orders", "pricing", "profile",
             "quotes", "reports", "returns", "reviews", "session", "shipping", "stock", "tax", "wallet"]
    names = rng.sample([f"{w}-{k}" for w in words for k in ("api", "worker", "cron")], N_SERVICES)
    files = {"docs/CONTAINER_POLICY.md": POLICY, "docs/APPROVED_BASES.md": approved_md()}
    truth = {"seed": seed, "services": {}}
    for name in names:
        dockerfile, readme, facts = build(rng_for(seed, "svc", name), name)
        files[f"services/{name}/Dockerfile"] = dockerfile
        files[f"services/{name}/README.md"] = readme
        truth["services"][name] = {**facts, "unit_chars": len(dockerfile) + len(readme) + 3000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
    return truth


def check(text, facts):
    """Which policy rules a Dockerfile breaks, plus whether it kept its behaviour."""
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    # Join continuation lines.
    joined, buf = [], ""
    for line in lines:
        buf += (" " if buf else "") + line.rstrip("\\").strip()
        if not line.endswith("\\"):
            joined.append(buf)
            buf = ""
    stages = [i for i, line in enumerate(joined) if line.upper().startswith("FROM ")]
    final = joined[stages[-1]:] if stages else joined
    broken = set()
    for i in stages:
        ref = joined[i].split()[1]
        m = re.match(r"([^@]+)@(sha256:[0-9a-f]{64})$", ref)
        if not m or m.group(1) not in BASES or m.group(2) != digest(m.group(1)):
            broken.add("R1")
    users = [line.split()[1] for line in final if line.upper().startswith("USER ")]
    if not users or users[-1] in ("root", "0", "0:0"):
        broken.add("R2")
    for line in joined:
        if line.split()[0].upper() in ("ENV", "ARG") and SECRET_RE.search(line):
            broken.add("R3")
    for line in joined:
        if re.search(r"(curl|wget)[^|]*\|\s*(sh|bash)", line):
            broken.add("R4")
    if facts["tool"] and not any(f"apt-get install" in line and TOOLS[facts["tool"]] in line for line in joined):
        broken.add("R4")
    if any(line.upper().startswith("EXPOSE") for line in final):
        hc = [line for line in final if line.upper().startswith("HEALTHCHECK")]
        want = f"localhost:{facts['port']}{facts['health']}"
        if not hc or want not in hc[-1]:
            broken.add("R5")
    for line in joined:
        if "apt-get install" in line and ("--no-install-recommends" not in line or "/var/lib/apt/lists" not in line):
            broken.add("R6")
    kept = all(any(k.strip() == line for line in joined) for k in facts["keep"])
    harmless_kept = any(line.startswith("ENV ") and not SECRET_RE.search(line) for line in joined)
    return broken, kept and harmless_kept


def grade(seed, workspace):
    """Per service, all or nothing: no policy rule broken, and every behaviour
    line (COPY, CMD, ENTRYPOINT, EXPOSE, WORKDIR) and the harmless ENV kept."""
    truth = generate(seed)
    per = {}
    for name, facts in truth["services"].items():
        path = Path(workspace) / "services" / name / "Dockerfile"
        if not path.exists():
            per[name] = 0.0
            continue
        broken, kept = check(path.read_text(), facts)
        per[name] = float(not broken and kept)
    return {"reward": round(sum(per.values()) / len(per), 4), "services": per}


def fixed(facts, text):
    out = []
    for line in text.splitlines():
        word = line.split(" ")[0]
        if word == "FROM":
            parts = line.split()
            image = parts[1].split("@")[0]
            image = DEPRECATED.get(image, image)
            parts[1] = f"{image}@{digest(image)}"
            line = " ".join(parts)
        elif word in ("ENV", "ARG") and SECRET_RE.search(line):
            continue
        elif "| sh" in line:
            line = (f"RUN apt-get update && apt-get install -y --no-install-recommends {TOOLS[facts['tool']]} "
                    "&& rm -rf /var/lib/apt/lists/*")
        elif "apt-get install" in line and "--no-install-recommends" not in line:
            line = ("RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates "
                    "&& rm -rf /var/lib/apt/lists/*")
        elif line == "USER root":
            continue
        out.append(line)
    tail = out.pop()  # CMD / ENTRYPOINT
    if not any(line.startswith("USER ") for line in out):
        alpine = "alpine" in facts["base"]
        out += ["RUN adduser -D -u 10001 app" if alpine else "RUN useradd --uid 10001 --create-home app", "USER app"]
    if facts["exposes"]:
        out.append(f"HEALTHCHECK CMD curl -fsS http://localhost:{facts['port']}{facts['health']} || exit 1")
    out.append(tail)
    return "\n".join(out) + "\n"


def solve(seed, workspace):
    truth = generate(seed)
    for name, facts in truth["services"].items():
        path = Path(workspace) / "services" / name / "Dockerfile"
        path.write_text(fixed(facts, path.read_text()))


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [s["unit_chars"] for s in t["services"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(POLICY) + 1500}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Container policy compliance

The platform team's scanner now blocks deploys that break
`docs/CONTAINER_POLICY.md`. Bring every Dockerfile under
`/workspace/services/` into compliance before Friday's release freeze.
Approved base images and digests are in `docs/APPROVED_BASES.md`.

Do not change what any service does.
"""

META = {
    "unit": "Dockerfile", "kind": "file hardening", "domain": "container images", "output_tokens": 1500, "needs_pytest": False,
    "failure_mode": "applying a policy precisely, per unit, with facts drawn from each unit's own docs",
    "deliverable": "edited `services/<svc>/Dockerfile` for 48 services",
    "grading": "Per service, all or nothing: the grader's policy checker finds no broken rule, and every "
               "COPY/CMD/ENTRYPOINT/EXPOSE/WORKDIR line and the harmless ENV survive. Reward is the mean.",
    "per_unit": "check all six rules against this Dockerfile, look up digests and successors, read the "
                "service README for its health endpoint, and edit without dropping behaviour",
    "traps": [
        "**Secrets by value, not name.** `ENV SECRET_ROTATION_DAYS=30` must stay; `ARG GITHUB_TOKEN=ghp_...` must go.",
        "**Deprecated tags** must move to their successor, and build stages need pinning too.",
        "**Health endpoints differ per service**; a generic `/health` check fails half of them.",
        "**`USER root` at the end** still breaks R2.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
