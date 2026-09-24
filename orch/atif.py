"""Reconstruct orchestrator telemetry from a Harbor ATIF trajectory.

This is what lets the system track score any scaffold Harbor runs, not just the
reference harness. For Claude Code (verified against harbor 0.23.0's converter):

- a spawn is a main-chain tool call named `Agent` (older builds: `Task`), whose
  arguments carry the brief as `prompt`;
- the worker's report comes back as that call's observation result;
- worker steps are flattened into the same step list and marked
  `extra.is_sidechain`, or embedded as `subagent_trajectories` (ATIF >= 1.7).

Worker tokens are attributed per worker when the trajectories are embedded, and
pooled into one `unattributed_worker_tokens` total when they are flattened.
Either way the totals are exact: they come from the provider's own counts.
"""

from datetime import datetime

SPAWN_TOOLS = {"Agent", "Task"}


def _text(content):
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    parts = []
    for part in content:
        if isinstance(part, dict):
            parts.append(str(part.get("text", "")))
        else:
            parts.append(str(part))
    return "\n".join(parts)


def _ts(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _tokens(step):
    metrics = step.get("metrics") or {}
    prompt = (metrics.get("prompt_tokens") or 0) + (metrics.get("cached_tokens") or 0)
    return prompt, metrics.get("completion_tokens") or 0, metrics.get("cost_usd") or 0.0


def _is_sidechain(step):
    return bool((step.get("extra") or {}).get("is_sidechain"))


def _agent_totals(steps):
    inp = out = 0
    cost = 0.0
    peak = 0
    for step in steps:
        prompt, completion, usd = _tokens(step)
        inp += prompt
        out += completion
        cost += usd
        peak = max(peak, prompt)
    return inp, out, cost, peak


def telemetry_from_atif(trajectory, task_id="", family=None, mode="delegate"):
    steps = trajectory.get("steps") or []
    main = [s for s in steps if not _is_sidechain(s)]
    side = [s for s in steps if _is_sidechain(s)]

    workers, by_call = [], {}
    lead_step = 0
    for step in main:
        if step.get("source") == "agent":
            lead_step += 1
        calls = [c for c in (step.get("tool_calls") or []) if c.get("function_name") in SPAWN_TOOLS]
        for call in calls:
            args = call.get("arguments") or {}
            worker = {
                "role": "worker",
                "id": f"a{len(workers) + 1}",
                "brief": str(args.get("prompt") or args.get("description") or ""),
                "steps": 0, "context_peak": 0, "input_tokens": 0, "output_tokens": 0,
                "cost_usd": 0.0, "exit_status": "", "report": "",
                "started": _ts(step.get("timestamp")) or 0.0, "finished": 0.0,
                "spawned_at_lead_step": lead_step,
                "same_turn_as": len(calls),
            }
            workers.append(worker)
            by_call[call.get("tool_call_id")] = worker
        for result in ((step.get("observation") or {}).get("results") or []):
            worker = by_call.get(result.get("source_call_id"))
            if worker is not None:
                worker["report"] = _text(result.get("content"))
                worker["exit_status"] = "Submitted" if worker["report"] else "no report"
                worker["finished"] = _ts(step.get("timestamp")) or worker["started"]

    embedded = {t.get("trajectory_id"): t for t in trajectory.get("subagent_trajectories") or []}
    unattributed = None
    if embedded:
        for step in main:
            for result in ((step.get("observation") or {}).get("results") or []):
                worker = by_call.get(result.get("source_call_id"))
                for ref in result.get("subagent_trajectory_ref") or []:
                    sub = embedded.get(ref.get("trajectory_id"))
                    if worker is None or sub is None:
                        continue
                    sub_steps = sub.get("steps") or []
                    inp, out, cost, peak = _agent_totals(sub_steps)
                    worker.update(input_tokens=inp, output_tokens=out, cost_usd=cost,
                                  context_peak=peak,
                                  steps=sum(1 for s in sub_steps if s.get("source") == "agent"))
    elif side:
        inp, out, cost, _ = _agent_totals(side)
        unattributed = {"input_tokens": inp, "output_tokens": out, "cost_usd": cost,
                        "steps": sum(1 for s in side if s.get("source") == "agent")}

    inp, out, cost, peak = _agent_totals(main)
    times = [t for t in (_ts(s.get("timestamp")) for s in steps) if t]
    lead = {
        "role": "lead", "id": "lead", "brief": "", "steps": lead_step,
        "context_peak": peak, "input_tokens": inp, "output_tokens": out, "cost_usd": cost,
        "exit_status": "", "report": "",
        "started": min(times) if times else 0.0, "finished": max(times) if times else 0.0,
        "spawned_at_lead_step": 0,
    }
    return {
        "schema": "subagent-bench/orch-telemetry/1",
        "task_id": task_id,
        "family": family,
        "mode": mode,
        "source": "atif",
        "limits": None,
        "worker_limits": None,
        "lead": lead,
        "workers": workers,
        "unattributed_worker_tokens": unattributed,
        "wall_clock_sec": round(max(times) - min(times), 3) if times else None,
        "tokens_exact": True,
        "oracle_is_solo": False,
    }
