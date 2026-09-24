"""Scripted orchestration policies for the rehearsal. No model, no key.

Each policy is a mini-compatible "model" that issues real bash commands through
the real reference harness: real caps, real `subagent` interception, real
workers, real verifier. What is simulated is *reading*: an agent that has
actually seen a ticket (or a service's status, components and logs) in an
observation knows the right answer for it, because it looks it up in the
ground truth.

That makes every agent a perfect reader, which is the point. With reading
skill held perfect, any difference between policies comes from structure: who
hits a wall, what gets partitioned, what survives synthesis. Those are the
effects the metrics claim to measure, and the rehearsal checks that they do.
It says nothing about any real model. In particular solo-xl scores as well as
delegate here, because a perfect reader suffers no context rot. Whether a real
model does is what the live run is for (ORCHESTRATOR.md 7).

Systems:

    solo          grep to narrow, then read candidates one by one; writes as it goes
    solo-xl       the same policy, 8x the context and steps
    judicious     delegates W, P and C (C with the record contract in every brief);
                  follows the L chain itself
    eager         always delegates, finely: C briefs carry no shared contract, and L
                  becomes a relay of workers
    sloppy        delegates W, P and C but leaves a gap, duplicates a group, and drops
                  findings during synthesis
    oracle-split  the harness's scripted lead with perfect-reader workers
"""

import json
import random
import re

from orch.families import chain, coupled, probe, wide
from orch.harness import SUBMIT_MARKER

KEYWORDS = "twice|two times|duplicate|double|again|second"
_FOOTER = re.compile(r"\n\[context: .*?\]\s*$", re.S)


class PolicyContext:
    def __init__(self, task):
        self.task = task
        self.rng = random.Random(f"policy:{task.id}")
        if task.family == "W":
            self.positives = {m["ticket"]: m["order"] for m in task.truth["matches"]}
        if task.family == "P":
            self.services = task.truth["services"]


class PolicyModel:
    """Drives a generator policy as a mini model.

    The generator yields bash commands and is sent each observation. Its return
    value is the worker's report (workers) or ignored (leads); either way the
    model then submits.
    """

    def __init__(self, policy, ctx, role):
        self._policy = policy
        self._ctx = ctx
        self._role = role
        self._gen = None
        self._done = False
        self._report = ""
        self.config = type("Config", (), {"model_name": f"policy:{policy.__name__}"})()

    def _action(self, command):
        # The command goes in the message text too, as a text-based model emits it:
        # what an agent writes costs it context just like what it reads.
        return {"role": "assistant", "content": f"```bash\n{command}\n```",
                "extra": {"actions": [{"command": command}], "cost": 0.0}}

    def query(self, messages, **kwargs):
        if self._done:
            return self._submit()
        observation = _FOOTER.sub("", str(messages[-1].get("content", "")))
        try:
            if self._gen is None:
                brief = str(messages[1].get("content", ""))
                self._gen = self._policy(self._ctx, brief)
                command = next(self._gen)
            else:
                command = self._gen.send(observation)
        except StopIteration as stop:
            self._done = True
            self._report = stop.value or ""
            return self._submit()
        return self._action(command)

    def _submit(self):
        if self._role == "worker":
            return self._action(f"cat <<'EOF'\n{SUBMIT_MARKER}\n{self._report}\nEOF")
        return self._action(f"echo {SUBMIT_MARKER}")

    def format_message(self, **kwargs):
        return dict(kwargs)

    def format_observation_messages(self, message, outputs, template_vars=None):
        body = "\n".join(str(o.get("output", "")) for o in outputs)
        return [{"role": "user", "content": body}]

    def get_template_vars(self, **kwargs):
        return {}

    def serialize(self):
        return {}


# --- shared pieces ---------------------------------------------------------------

def _write_json(obj):
    return f"cat > answer.json <<'EOF'\n{json.dumps(obj)}\nEOF"


def _json_lines(text, required):
    out = []
    for line in text.splitlines():
        line = line.strip().strip(",")
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
            except ValueError:
                continue
            if isinstance(obj, dict) and set(required) <= set(obj):
                out.append(obj)
    return out


def _read_tickets(ctx, tickets, write_as_you_go):
    found = {}
    for tid in tickets:
        obs = yield f"cat tickets/{tid}.txt"
        if f"Ticket {tid}" in obs and tid in ctx.positives:
            found[tid] = ctx.positives[tid]
            if write_as_you_go:
                yield _write_json({"matches": [{"ticket": t, "order": o}
                                               for t, o in sorted(found.items())]})
    return found


def _diagnose(ctx, services, write_as_you_go):
    found = {}
    for svc in services:
        truth = ctx.services[svc]
        status = yield f"svcctl status {svc}"
        comps = yield f"svcctl components {svc}"
        if "incident notes" not in status or truth["component"] not in comps:
            continue
        logs = yield f"svcctl logs {svc} {truth['component']}"
        if "ERROR" in logs:
            found[svc] = dict(truth)
            if write_as_you_go:
                yield _write_json({"services": found})
    return found


def _ticket_candidates(obs):
    return sorted({m for m in re.findall(r"tickets/(T-\d+)\.txt", obs)})


def _services_from(instruction):
    return re.findall(r"`([a-z][a-z0-9-]+)`", instruction.split("\n")[0])


def _chunks(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def _spawn_block(briefs):
    return "\n".join(f"subagent spawn <<'BRIEF'\n{b}\nBRIEF" for b in briefs)


# --- solo -----------------------------------------------------------------------------

def solo(ctx, instruction):
    family = ctx.task.family
    if family == "W":
        obs = yield f"grep -liE '{KEYWORDS}' tickets/*.txt"
        yield from _read_tickets(ctx, _ticket_candidates(obs), write_as_you_go=True)
    elif family == "P":
        yield from _diagnose(ctx, _services_from(instruction), write_as_you_go=True)
    elif family == "C":
        yield from _write_core(ctx, coupled.REPRESENTATIONS[0])
        yield from _write_views(ctx, ctx.task.work_items, coupled.REPRESENTATIONS[0])
        yield "python -m unittest discover tests"
    elif family == "L":
        yield from _follow(ctx, ctx.task.truth["path"][0], len(ctx.task.truth["path"]),
                           write_every=20)


def _write_core(ctx, rep):
    yield "cat jobs/producer.py jobs/scheduler.py jobs/store.py"
    for module in ("producer", "scheduler"):
        yield f"cat > jobs/{module}.py <<'PYEOF'\n{coupled.render_core(module, *rep)}PYEOF"


def _write_views(ctx, names, rep):
    views = ctx.task.truth["views"]
    for name in names:
        spec = yield f"cat docs/views/{name}.md"
        yield f"cat views/{name}.py"
        if "Priority marker" in spec:
            yield f"cat > views/{name}.py <<'PYEOF'\n{coupled.render_view(name, views[name], *rep)}PYEOF"


def _follow(ctx, start, hops, write_every=None):
    """Follow the chain from `start` for up to `hops` pages; returns (path, closing code)."""
    path_truth = ctx.task.truth["path"]
    i = path_truth.index(start)
    path, closing = [], None
    while len(path) < hops and i < len(path_truth):
        code = path_truth[i]
        obs = yield f"cat ledger/{code}.txt"
        if f"Ledger page {code}" not in obs:
            break
        path.append(code)
        if "Closing code:" in obs:
            closing = obs.split("Closing code:")[1].split()[0]
            break
        i += 1
        if write_every and len(path) % write_every == 0:
            yield _write_json({"path": path})
    if write_every:
        yield _write_json({"path": path, "closing_code": closing or ""})
    return path, closing


# --- workers ------------------------------------------------------------------------

def worker(ctx, brief):
    family = ctx.task.family
    if family == "W":
        tickets = re.findall(r"tickets/(T-\d+)\.txt", brief)
        found = yield from _read_tickets(ctx, tickets, write_as_you_go=False)
        lines = [json.dumps({"ticket": t, "order": o}) for t, o in sorted(found.items())]
        return "\n".join(lines) or "None of these tickets count."
    if family == "P":
        services = re.findall(r"services: ([^.]+)\.", brief)[0].split(", ")
        found = yield from _diagnose(ctx, services, write_as_you_go=False)
        return "\n".join(json.dumps({"service": s, **v}) for s, v in found.items())
    if family == "C":
        if "under the key 'priority'" in brief:
            rep = coupled.REPRESENTATIONS[0]
        else:
            # No contract in the brief: an isolated worker picks a representation itself.
            rep = random.Random(f"{ctx.task.id}:{brief}").choice(coupled.REPRESENTATIONS)
        views = coupled.views_in(brief)
        if views:
            yield from _write_views(ctx, views, rep)
        else:
            yield from _write_core(ctx, rep)
        yield "python -m unittest discover tests"
        return f"Updated {', '.join(views) or 'producer and scheduler'}; priority stored as {rep}."
    if family == "L":
        start = re.findall(r"ledger/(P-\d+)\.txt", brief)[0]
        hops = int(re.findall(r"for (\d+) hops", brief)[0])
        path, closing = yield from _follow(ctx, start, hops)
        return "\n".join(path) + (f"\nclosing code: {closing}" if closing else "")
    return "nothing to do"


# --- delegating leads ------------------------------------------------------------------

def _spread(groups, gap, duplicate):
    if gap and len(groups) > 1:
        groups = groups[:-1]
    if duplicate and groups:
        groups = groups + [groups[0]]
    return groups


def _fan_out_w(ctx, group, gap=False, duplicate=False, keep_per_report=None):
    obs = yield "ls tickets"
    items = sorted(n[:-4] for n in obs.split() if n.endswith(".txt"))
    groups = _spread(_chunks(items, group), gap, duplicate)
    briefs = [wide.WORKER_BRIEF.format(files=", ".join(f"tickets/{t}.txt" for t in g))
              for g in groups]
    yield _spawn_block(briefs)
    reports = yield "subagent wait"
    found = {}
    for block in reports.split("=== ")[1:]:
        rows = _json_lines(block, ("ticket", "order"))
        for row in rows[:keep_per_report] if keep_per_report else rows:
            found[row["ticket"]] = row["order"]
    yield _write_json({"matches": [{"ticket": t, "order": o} for t, o in sorted(found.items())]})


def _fan_out_p(ctx, instruction, group, gap=False, duplicate=False, keep_per_report=None):
    groups = _spread(_chunks(_services_from(instruction), group), gap, duplicate)
    briefs = [probe.WORKER_BRIEF.format(services=", ".join(g), menu=probe.MENU) for g in groups]
    yield _spawn_block(briefs)
    reports = yield "subagent wait"
    found = {}
    for block in reports.split("=== ")[1:]:
        rows = _json_lines(block, ("service", "component", "cause"))
        for row in rows[:keep_per_report] if keep_per_report else rows:
            found[row["service"]] = {"component": row["component"], "cause": row["cause"]}
    yield _write_json({"services": found})


VAGUE = "Keep it consistent with how the rest of the system stores priority."


def _fan_out_c(ctx, group, contract, gap=False, duplicate=False):
    names = ctx.task.work_items
    groups = _spread(_chunks(names, group), gap, duplicate)
    briefs = [coupled.CORE_BRIEF.format(contract=contract)] + [
        coupled.WORKER_BRIEF.format(files=", ".join(f"views/{n}.py" for n in g), contract=contract)
        for g in groups]
    yield _spawn_block(briefs)
    yield "subagent wait"
    yield "python -m unittest discover tests"


def _relay_l(ctx, segments):
    """Delegate a sequential chain as a relay: each worker continues where the last stopped."""
    path_len = len(ctx.task.truth["path"])
    hops = -(-path_len // segments)
    start, path, closing = ctx.task.truth["path"][0], [], None
    for _ in range(segments):
        report = yield ("subagent run <<'BRIEF'\n"
                        + chain.SEGMENT_BRIEF.format(start=start, hops=hops) + "BRIEF")
        pages = re.findall(r"^(P-\d+)$", report, re.M)
        if not pages:
            break
        path += pages if not path else pages[1:]
        match = re.search(r"closing code: (\S+)", report)
        if match:
            closing = match.group(1)
            break
        start = pages[-1]
        hops += 1  # the next worker re-reads its starting page
    yield _write_json({"path": path, "closing_code": closing or ""})


def judicious(ctx, instruction):
    family = ctx.task.family
    if family == "W":
        yield from _fan_out_w(ctx, wide.TICKETS_PER_WORKER)
    elif family == "P":
        yield from _fan_out_p(ctx, instruction, probe.SERVICES_PER_WORKER)
    elif family == "C":
        yield from _fan_out_c(ctx, coupled.VIEWS_PER_WORKER, coupled.CONTRACT)
    else:
        yield from solo(ctx, instruction)


def eager(ctx, instruction):
    """Fans out everything, finely, with no shared contract."""
    family = ctx.task.family
    if family == "W":
        yield from _fan_out_w(ctx, 6)
    elif family == "P":
        yield from _fan_out_p(ctx, instruction, 2)
    elif family == "C":
        yield from _fan_out_c(ctx, 2, VAGUE)
    elif family == "L":
        yield from _relay_l(ctx, 4)


def sloppy(ctx, instruction):
    """Delegates the right families, but partitions and merges carelessly."""
    family = ctx.task.family
    if family == "W":
        yield from _fan_out_w(ctx, 16, gap=True, duplicate=True, keep_per_report=2)
    elif family == "P":
        yield from _fan_out_p(ctx, instruction, 4, gap=True, duplicate=True, keep_per_report=2)
    elif family == "C":
        yield from _fan_out_c(ctx, 4, coupled.CONTRACT, gap=True, duplicate=True)
    else:
        yield from solo(ctx, instruction)


LEADS = {
    "solo": ("solo", solo),
    "solo-xl": ("solo-xl", solo),
    "judicious": ("delegate", judicious),
    "eager": ("delegate", eager),
    "sloppy": ("delegate", sloppy),
    "oracle-split": ("oracle-split", solo),
}


def build(system, task):
    """(mode, lead_model, worker_model_factory) for one rehearsal system."""
    mode, lead_policy = LEADS[system]
    ctx = PolicyContext(task)
    lead = PolicyModel(lead_policy, ctx, role="lead")
    return mode, lead, (lambda: PolicyModel(worker, ctx, role="worker"))
