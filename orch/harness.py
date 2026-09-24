"""Reference harness for the orchestrator track (ORCHESTRATOR.md 6).

mini-swe-agent, bash-only, with one pseudo-command the harness intercepts
before it reaches the container:

    subagent spawn <<'EOF'      start a worker in the background; prints its id
    <brief>
    EOF
    subagent wait [id ...]      block until workers finish; prints their reports
    subagent run <<'EOF'        spawn one worker and wait for it
    <brief>
    EOF

Several spawns may share one command; that is how a bash-only model expresses
parallelism. Workers share the container's filesystem but nothing else. They
have their own context and step budget, cannot spawn further workers, and
finish with a written report.

Every agent -- lead or worker -- runs under the same explicit limits: a context
cap checked before each model call, a step cap, and a per-observation character
cap. Every observation ends with a usage footer, in every condition, so an agent
can plan around its own wall.

Four conditions, one code path (ORCHESTRATOR.md 4):

    solo          no subagent command
    solo-xl       no subagent command, context and steps x XL_MULTIPLIER
    delegate      subagent command documented; the model decides
    oracle-split  a scripted lead: the task's ideal partition and briefs, real
                  workers, scripted merge. Defined for W and P; on C and S the
                  ideal policy is not to delegate, so it runs solo.

mini is imported lazily, so everything that only reads telemetry works without it.
"""

import json
import re
import shlex
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from orch.task import DEFAULT_LIMITS, approx_tokens

MODES = ("solo", "solo-xl", "delegate", "oracle-split")
XL_MULTIPLIER = 8
SUBMIT_MARKER = "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"

# --- prompts -----------------------------------------------------------------

LEAD_SYSTEM = """You are an autonomous agent working in a Linux container. Your working \
directory holds the task's files. You have one tool: bash. Run one command per step.

Limits (enforced):
- Your context window is {context_tokens} tokens. Every observation ends with a footer \
showing how much you have used. If you go past the limit you stop immediately, and only \
what you have already written to disk counts.
- You have at most {step_limit} steps.
- Long command output is truncated to {observation_chars} characters (head and tail kept).

When the task is complete, run `echo {marker}` as a command on its own.
"""

DELEGATE_ADDENDUM = """
You can delegate work to subagents with the `subagent` command. It must be the \
only thing in its command:

    subagent spawn <<'EOF'
    <brief>
    EOF

starts a subagent in the background and prints its id. Several `subagent spawn` \
blocks can go in one command. `subagent wait` blocks until all running subagents \
finish and prints their reports (`subagent wait a1 a3` waits for specific ones). \
`subagent run <<'EOF' ... EOF` spawns one and waits for it.

Each subagent is an agent like you with its own fresh {context_tokens}-token \
context and its own {step_limit}-step budget. It shares this container's \
filesystem but sees none of your conversation: the brief is all it knows. It \
returns a written report. At most {max_concurrent_subagents} run at once and \
{max_total_subagents} in total. Subagents cannot spawn subagents. Delegation costs \
tokens and time, so use it when it helps.
"""

LEAD_INSTANCE = "{{ task }}"

WORKER_SYSTEM = """You are a subagent. A lead agent delegated one scoped task to you and \
is waiting for your report. You cannot ask it questions, and it cannot see your \
work: your report is the only thing that goes back.

You work in a Linux container, in the same working directory as the lead. You have \
one tool: bash. Run one command per step.

Limits (enforced): a {context_tokens}-token context window (every observation ends \
with a usage footer; past the limit you stop and your report is lost), at most \
{step_limit} steps, and output truncated to {observation_chars} characters.

Finish by printing your report as a command on its own:

    cat <<'EOF'
    {marker}
    <your report>
    EOF

Report what you established and where you found it. Say plainly what you could not \
establish. Do only what the brief asks.
"""

WORKER_INSTANCE = "{{ task }}"


# --- the subagent command ----------------------------------------------------

_HEREDOC = re.compile(r"^\s*subagent\s+(spawn|run)\s*<<-?\s*(['\"]?)(\w+)\2\s*$")
_INLINE = re.compile(r"^\s*subagent\s+(spawn|run)\s+(.+)$")
_WAIT = re.compile(r"^\s*subagent\s+wait\b(.*)$")


class SubagentSyntaxError(ValueError):
    pass


def is_subagent_command(command):
    for line in (command or "").splitlines():
        if line.strip():
            return line.strip().split()[0] == "subagent"
    return False


def parse_subagent_command(command):
    """Parse a command made only of subagent operations.

    Returns [("spawn"|"run", brief) | ("wait", [ids])]. Raises
    SubagentSyntaxError on anything else -- mixing subagent operations with
    ordinary shell is refused rather than half-executed.
    """
    lines = command.splitlines()
    ops, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        heredoc = _HEREDOC.match(line)
        if heredoc:
            verb, _, delim = heredoc.groups()
            body, i = [], i + 1
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            if i == len(lines):
                raise SubagentSyntaxError(f"heredoc not terminated by {delim}")
            i += 1
            brief = "\n".join(body).strip()
            if not brief:
                raise SubagentSyntaxError("empty brief")
            ops.append((verb, brief))
            continue
        wait = _WAIT.match(line)
        if wait:
            ops.append(("wait", wait.group(1).split()))
            i += 1
            continue
        inline = _INLINE.match(line)
        if inline:
            verb, rest = inline.groups()
            try:
                brief = " ".join(shlex.split(rest)).strip()
            except ValueError as exc:
                raise SubagentSyntaxError(str(exc)) from exc
            if not brief:
                raise SubagentSyntaxError("empty brief")
            ops.append((verb, brief))
            i += 1
            continue
        raise SubagentSyntaxError(
            f"not a subagent operation: {line.strip()[:80]!r}. Issue subagent "
            "commands on their own, not mixed with other shell commands."
        )
    if not ops:
        raise SubagentSyntaxError("no operation")
    return ops


# --- limits and per-agent accounting -------------------------------------------

@dataclass
class Limits:
    context_tokens: int = DEFAULT_LIMITS["context_tokens"]
    step_limit: int = DEFAULT_LIMITS["step_limit"]
    observation_chars: int = DEFAULT_LIMITS["observation_chars"]
    max_concurrent_subagents: int = DEFAULT_LIMITS["max_concurrent_subagents"]
    max_total_subagents: int = DEFAULT_LIMITS["max_total_subagents"]

    @classmethod
    def from_dict(cls, data):
        known = {k: v for k, v in (data or {}).items() if k in cls.__dataclass_fields__}
        return cls(**known)

    def scaled(self, factor):
        return Limits(
            context_tokens=self.context_tokens * factor,
            step_limit=self.step_limit * factor,
            observation_chars=self.observation_chars,
            max_concurrent_subagents=self.max_concurrent_subagents,
            max_total_subagents=self.max_total_subagents,
        )

    def as_prompt_vars(self):
        return dict(self.__dict__, marker=SUBMIT_MARKER)


@dataclass
class AgentStats:
    role: str
    id: str
    brief: str = ""
    steps: int = 0
    context_peak: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    exit_status: str = ""
    report: str = ""
    started: float = 0.0
    finished: float = 0.0
    spawned_at_lead_step: int = 0

    def as_dict(self):
        return dict(self.__dict__)


def context_size(messages):
    total = 0
    for message in messages:
        content = message.get("content")
        if isinstance(content, list):
            content = " ".join(str(part.get("text", part)) for part in content)
        total += approx_tokens(str(content or ""))
        for call in message.get("tool_calls") or []:
            total += approx_tokens(json.dumps(call))
    return total


def truncate(text, limit):
    if len(text) <= limit:
        return text
    head = limit * 2 // 3
    tail = limit - head
    dropped = len(text) - limit
    return f"{text[:head]}\n[... {dropped} characters truncated ...]\n{text[-tail:]}"


def _mini():
    from minisweagent.agents.default import DefaultAgent
    from minisweagent.exceptions import LimitsExceeded, Submitted

    return DefaultAgent, LimitsExceeded, Submitted


def build_capped_agent(model, env, limits, stats, system_template, instance_template):
    """A mini DefaultAgent that enforces the context cap and prints a usage footer."""
    DefaultAgent, LimitsExceeded, _ = _mini()

    class CappedAgent(DefaultAgent):
        def query(self):
            used = context_size(self.messages)
            stats.context_peak = max(stats.context_peak, used)
            if used > limits.context_tokens:
                raise LimitsExceeded({
                    "role": "exit", "content": "ContextExceeded",
                    "extra": {"exit_status": "ContextExceeded", "submission": ""},
                })
            if self.n_calls >= limits.step_limit:
                raise LimitsExceeded({
                    "role": "exit", "content": "StepLimitExceeded",
                    "extra": {"exit_status": "StepLimitExceeded", "submission": ""},
                })
            stats.input_tokens += used
            message = super().query()
            stats.steps = self.n_calls
            stats.cost_usd = self.cost
            stats.output_tokens += approx_tokens(
                str(message.get("content") or "")
                + json.dumps(message.get("extra", {}).get("actions", []))
            )
            return message

        def execute_actions(self, message):
            added = super().execute_actions(message)
            if added and isinstance(added[-1].get("content"), str):
                used = context_size(self.messages)
                added[-1]["content"] += (
                    f"\n[context: {used / 1000:.1f}k / {limits.context_tokens / 1000:.0f}k "
                    f"tokens | step {self.n_calls} / {limits.step_limit}]"
                )
            return added

    return CappedAgent(
        model, env,
        system_template=system_template.format(**limits.as_prompt_vars()),
        instance_template=instance_template,
        step_limit=0,  # enforced in query() so the exit status is ours
        cost_limit=0.0,
    )


# --- environment wrapper -------------------------------------------------------

class DelegatingEnv:
    """Wraps any mini environment: truncation, submission, and `subagent`.

    `pool` is None for solo leads and for workers; then `subagent` behaves like
    a command that does not exist, and is never run in the container.
    """

    def __init__(self, base, limits, pool=None, lead_stats=None):
        self.base = base
        self.limits = limits
        self.pool = pool
        self.lead_stats = lead_stats

    @staticmethod
    def command_of(action):
        if isinstance(action, dict):
            return action.get("command", "")
        return str(action or "")

    def execute(self, action, cwd="", **kwargs):
        _, _, Submitted = _mini()
        command = self.command_of(action)
        if is_subagent_command(command):
            return self._subagent(command)
        # A base env that detects submission itself (mini's LocalEnvironment)
        # raises Submitted from here; one that doesn't (the Harbor bridge) is
        # handled below, so both behave the same.
        result = self.base.execute(action)
        output = str(result.get("output", ""))
        lines = output.lstrip().splitlines()
        if lines and lines[0].strip() == SUBMIT_MARKER and result.get("returncode", 0) == 0:
            submission = "\n".join(lines[1:])
            raise Submitted({
                "role": "exit", "content": submission,
                "extra": {"exit_status": "Submitted", "submission": submission},
            })
        result = dict(result)
        result["output"] = truncate(output, self.limits.observation_chars)
        return result

    def _subagent(self, command):
        if self.pool is None:
            return {"output": "bash: subagent: command not found", "returncode": 127}
        try:
            ops = parse_subagent_command(command)
        except SubagentSyntaxError as exc:
            return {"output": f"subagent: {exc}", "returncode": 2}
        out = []
        step = self.lead_stats.steps if self.lead_stats else 0
        for verb, arg in ops:
            if verb == "spawn":
                out.append(self.pool.spawn(arg, step))
            elif verb == "run":
                started = self.pool.spawn(arg, step)
                ids = re.findall(r"\ba\d+\b", started)
                out.append(started if not ids else self.pool.wait(ids[:1]))
            else:
                out.append(self.pool.wait(arg or None))
        return {"output": "\n".join(out), "returncode": 0}

    def get_template_vars(self, **kwargs):
        getter = getattr(self.base, "get_template_vars", None)
        return getter(**kwargs) if getter else {}

    def serialize(self):
        getter = getattr(self.base, "serialize", None)
        return getter() if getter else {}


# --- workers -------------------------------------------------------------------

class SubagentPool:
    def __init__(self, base_env, worker_model_factory, limits, telemetry_sink):
        self.base_env = base_env
        self.model_factory = worker_model_factory
        self.limits = limits
        self.workers = []           # AgentStats, in spawn order
        self._threads = {}
        self._agents = {}
        self._lock = threading.Lock()
        self._slots = threading.Semaphore(limits.max_concurrent_subagents)
        self._sink = telemetry_sink

    def spawn(self, brief, lead_step=0):
        with self._lock:
            if len(self.workers) >= self.limits.max_total_subagents:
                return (f"subagent: limit of {self.limits.max_total_subagents} subagents "
                        "reached; nothing spawned")
            wid = f"a{len(self.workers) + 1}"
            stats = AgentStats(role="worker", id=wid, brief=brief, spawned_at_lead_step=lead_step)
            self.workers.append(stats)
        thread = threading.Thread(target=self._run, args=(stats,), daemon=True)
        self._threads[wid] = thread
        thread.start()
        return f"spawned {wid}"

    def _run(self, stats):
        with self._slots:
            stats.started = time.time()
            env = DelegatingEnv(self.base_env, self.limits, pool=None)
            agent = build_capped_agent(
                self.model_factory(), env, self.limits, stats, WORKER_SYSTEM, WORKER_INSTANCE
            )
            self._agents[stats.id] = agent
            try:
                result = agent.run(task=stats.brief)
                stats.exit_status = result.get("exit_status", "")
                stats.report = str(result.get("submission", "")).strip()
            except Exception as exc:  # noqa: BLE001 -- a crashed worker is a failed worker
                stats.exit_status = f"error: {type(exc).__name__}: {exc}"
            finally:
                stats.steps = agent.n_calls
                stats.cost_usd = agent.cost
                stats.finished = time.time()
                self._sink(stats, agent)

    def wait(self, ids=None):
        with self._lock:
            known = {w.id: w for w in self.workers}
        targets = ids or list(known)
        blocks = []
        for wid in targets:
            if wid not in known:
                blocks.append(f"=== {wid}: no such subagent ===")
                continue
            self._threads[wid].join()
            w = known[wid]
            report = w.report or "(no report)"
            blocks.append(
                f"=== {wid} ({w.exit_status}, {w.steps} steps) ===\n"
                + truncate(report, self.limits.observation_chars)
            )
        return "\n\n".join(blocks) if blocks else "no subagents"

    def join_all(self):
        for thread in list(self._threads.values()):
            thread.join()


# --- the run -------------------------------------------------------------------

@dataclass
class RunResult:
    mode: str
    telemetry: dict
    lead_exit: str
    logs_dir: Path = None
    extra: dict = field(default_factory=dict)


def _detect_family(instruction):
    if "svcctl" in instruction:
        return "P"
    if "tickets/" in instruction:
        return "W"
    return None


def run_orchestrated(instruction, base_env, lead_model, worker_model_factory, mode,
                     limits=None, logs_dir=None, task_id="", family=None):
    """Run one condition of one task. Returns RunResult with full telemetry.

    `base_env` is any mini-compatible environment already rooted at the task's
    workspace. Nothing here grades: the verifier does that from the workspace.
    """
    if mode not in MODES:
        raise ValueError(f"mode must be one of {MODES}")
    limits = limits or Limits()
    family = family or _detect_family(instruction)
    logs = Path(logs_dir) if logs_dir else None
    if logs:
        logs.mkdir(parents=True, exist_ok=True)

    lead_limits = limits.scaled(XL_MULTIPLIER) if mode == "solo-xl" else limits
    lead = AgentStats(role="lead", id="lead")
    trajectories = {}

    def sink(stats, agent):
        trajectories[stats.id] = agent.messages

    pool = None
    if mode in ("delegate", "oracle-split"):
        pool = SubagentPool(base_env, worker_model_factory, limits, sink)

    t0 = time.time()
    lead.started = t0
    if mode == "oracle-split" and family in ("W", "P"):
        lead.exit_status = _scripted_lead(instruction, base_env, pool, limits, family, lead)
    else:
        system = LEAD_SYSTEM
        if mode == "delegate":
            system = LEAD_SYSTEM + DELEGATE_ADDENDUM
        env = DelegatingEnv(base_env, lead_limits, pool=pool if mode == "delegate" else None,
                            lead_stats=lead)
        agent = build_capped_agent(lead_model, env, lead_limits, lead, system, LEAD_INSTANCE)
        try:
            result = agent.run(task=instruction)
            lead.exit_status = result.get("exit_status", "")
        except Exception as exc:  # noqa: BLE001
            lead.exit_status = f"error: {type(exc).__name__}: {exc}"
        lead.steps = agent.n_calls
        lead.cost_usd = agent.cost
        trajectories["lead"] = agent.messages
    if pool:
        pool.join_all()
    lead.finished = time.time()

    workers = pool.workers if pool else []
    telemetry = {
        "schema": "subagent-bench/orch-telemetry/1",
        "task_id": task_id,
        "family": family,
        "mode": mode,
        "source": "reference-harness",
        "limits": lead_limits.__dict__,
        "worker_limits": limits.__dict__,
        "lead": lead.as_dict(),
        "workers": [w.as_dict() for w in workers],
        "wall_clock_sec": round(lead.finished - t0, 3),
        "tokens_exact": False,
        "oracle_is_solo": mode == "oracle-split" and family not in ("W", "P"),
    }
    if logs:
        (logs / "telemetry.json").write_text(json.dumps(telemetry, indent=2))
        (logs / "trajectories.json").write_text(json.dumps(trajectories, indent=2, default=str))
    return RunResult(mode=mode, telemetry=telemetry, lead_exit=lead.exit_status, logs_dir=logs)


def _scripted_lead(instruction, base_env, pool, limits, family, lead):
    """oracle-split: the ideal partition and briefs, real workers, scripted merge."""
    from orch.families import probe, wide

    module = wide if family == "W" else probe
    if family == "W":
        listing = base_env.execute({"command": "ls tickets"})
        items = sorted(n[:-4] for n in str(listing.get("output", "")).split() if n.endswith(".txt"))
    else:
        items = re.findall(r"`([a-z][a-z0-9-]+)`", instruction.split("\n")[0])
    plan = module._plan(items)
    lead.steps = 1
    for part in plan:
        pool.spawn(part["brief"], lead.steps)
    pool.join_all()
    answer = module.merge_reports([w.report for w in pool.workers])
    payload = json.dumps(answer)
    base_env.execute({"command": f"cat > answer.json <<'ORCH_EOF'\n{payload}\nORCH_EOF"})
    lead.steps = 3
    return "Submitted"
