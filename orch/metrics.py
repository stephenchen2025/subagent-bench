"""Orchestrator-track metrics (ORCHESTRATOR.md 5).

Input is a list of run records, one per (system, condition, task):

    {"system", "condition", "task_id", "family", "size", "seed", "label",
     "work_items", "reward": {...}, "telemetry": {...},
     "answer": <answer.json or None>, "truth": <ground truth or None>}

`condition` is solo, solo-xl, oracle-split, or anything starting with
"delegate" (the rehearsal has several delegating policies, a real run has one).
Every delegate condition is compared against the same system's baselines.

Nothing here calls a model. Everything is recomputable from records on disk.
"""

import re
from collections import defaultdict
from statistics import mean

FAVOURABLE = ("W", "P", "C")
UNFAVOURABLE = ("L",)
BASELINES = ("solo", "solo-xl", "oracle-split")
MIN_CEILING_GAP = 0.05


def is_delegate(condition):
    return condition.startswith("delegate")


# --- per-run process metrics ------------------------------------------------------

def _mentions(text, item):
    return re.search(rf"(?<![\w-]){re.escape(item)}(?![\w-])", text or "") is not None


def coverage_and_duplication(telemetry, work_items):
    """Which work items appear in any brief, and which in more than one."""
    briefs = [w.get("brief", "") for w in telemetry.get("workers", [])]
    if not briefs or not work_items:
        return None, None
    counts = {item: sum(_mentions(b, item) for b in briefs) for item in work_items}
    covered = [i for i, c in counts.items() if c > 0]
    coverage = len(covered) / len(work_items)
    duplication = (sum(1 for i in covered if counts[i] > 1) / len(covered)) if covered else 0.0
    return coverage, duplication


def _reported_pairs(family, reports, truth):
    """Correct findings that some worker report states on a single line."""
    found = set()
    lines = [line for r in reports for line in (r or "").splitlines()]
    if family == "W":
        for match in truth.get("matches", []):
            t, o = match["ticket"], match["order"]
            if any(t in line and o in line for line in lines):
                found.add((t, o))
    elif family == "P":
        for svc, want in truth.get("services", {}).items():
            if any(_mentions(line, svc) and want["component"] in line and want["cause"] in line
                   for line in lines):
                found.add((svc, want["component"], want["cause"]))
    return found


def _final_pairs(family, answer):
    answer = answer or {}
    if family == "W":
        return {(m.get("ticket"), m.get("order")) for m in answer.get("matches", [])
                if isinstance(m, dict)}
    if family == "P":
        return {(s, v.get("component"), v.get("cause"))
                for s, v in (answer.get("services") or {}).items() if isinstance(v, dict)}
    return set()


def synthesis_loss(record):
    """Fraction of correct worker findings the final answer lost or changed.

    Approximate for free-text reports: a finding counts as reported when its ids
    appear together on one line of a report. JSON-line reports are exact.
    """
    family, truth = record["family"], record.get("truth")
    workers = record["telemetry"].get("workers", [])
    if family not in ("W", "P") or not truth or not workers:
        return None
    reported = _reported_pairs(family, [w.get("report", "") for w in workers], truth)
    if not reported:
        return None
    final = _final_pairs(family, record.get("answer"))
    return len(reported - final) / len(reported)


def peak_concurrency(workers):
    events = []
    for w in workers:
        if w.get("started") and w.get("finished"):
            events += [(w["started"], 1), (w["finished"], -1)]
    if not events:
        return max((w.get("same_turn_as", 0) for w in workers), default=0)
    level = peak = 0
    for _, delta in sorted(events, key=lambda e: (e[0], e[1])):
        level += delta
        peak = max(peak, level)
    return peak


def run_metrics(record):
    tel = record["telemetry"]
    lead, workers = tel["lead"], tel.get("workers", [])
    unattributed = tel.get("unattributed_worker_tokens") or {}
    worker_tokens = sum(w["input_tokens"] + w["output_tokens"] for w in workers) + \
        unattributed.get("input_tokens", 0) + unattributed.get("output_tokens", 0)
    lead_tokens = lead["input_tokens"] + lead["output_tokens"]
    coverage, duplication = coverage_and_duplication(tel, record.get("work_items") or [])
    cap = (tel.get("limits") or {}).get("context_tokens")
    return {
        "score": float(record["reward"].get("reward", 0.0)),
        "spawned": len(workers),
        "peak_concurrency": peak_concurrency(workers),
        "coverage": coverage,
        "duplication": duplication,
        "synthesis_loss": synthesis_loss(record),
        "lead_tokens": lead_tokens,
        "total_tokens": lead_tokens + worker_tokens,
        "lead_context_peak": lead["context_peak"],
        "lead_context_frac": (lead["context_peak"] / cap) if cap else None,
        "lead_exit": lead.get("exit_status", ""),
        "wall_clock_sec": tel.get("wall_clock_sec"),
        "cost_usd": lead.get("cost_usd", 0.0) + sum(w.get("cost_usd", 0.0) for w in workers)
        + unattributed.get("cost_usd", 0.0),
    }


# --- aggregation -------------------------------------------------------------------

def _avg(values):
    values = [v for v in values if v is not None]
    return mean(values) if values else None


def cells(records):
    """(system, condition, family, size) -> mean per-run metrics over seeds."""
    grouped = defaultdict(list)
    for record in records:
        key = (record["system"], record["condition"], record["family"], record["size"])
        grouped[key].append(run_metrics(record))
    out = {}
    for key, runs in grouped.items():
        out[key] = {k: _avg([r[k] for r in runs]) for k in runs[0] if k != "lead_exit"}
        out[key]["n"] = len(runs)
        out[key]["spawn_rate"] = mean(1.0 if r["spawned"] else 0.0 for r in runs)
    return out


def _ratio(num, den):
    if num is None or not den:
        return None
    return num / den


def summarise(records):
    """Headline metrics per (system, delegate condition). ORCHESTRATOR.md 5.1-5.3."""
    table = cells(records)
    systems = sorted({r["system"] for r in records})
    summary = {}
    for system in systems:
        conditions = sorted({r["condition"] for r in records if r["system"] == system})
        for cond in [c for c in conditions if is_delegate(c)]:
            summary[(system, cond)] = _summarise_one(system, cond, table, records)
    return summary, table


def _get(table, system, cond, family, size, field="score"):
    cell = table.get((system, cond, family, size))
    return None if cell is None else cell.get(field)


def _summarise_one(system, cond, table, records):
    sizes = sorted({(r["family"], r["size"]) for r in records if r["system"] == system})
    per_cell, lift_sum, gap_sum = [], 0.0, 0.0
    for family, size in sizes:
        if family not in FAVOURABLE:
            continue
        solo = _get(table, system, "solo", family, size)
        xl = _get(table, system, "solo-xl", family, size)
        dele = _get(table, system, cond, family, size)
        oracle = _get(table, system, "oracle-split", family, size)
        ceiling = oracle if oracle is not None else 1.0
        if dele is None or solo is None:
            continue
        gap = ceiling - solo
        capture = (dele - solo) / gap if gap >= MIN_CEILING_GAP else None
        if capture is not None:
            lift_sum += dele - solo
            gap_sum += gap
        per_cell.append({
            "family": family, "size": size, "solo": solo, "solo_xl": xl, "delegate": dele,
            "oracle": oracle, "lift": dele - solo,
            "structural_lift": None if xl is None else dele - xl,
            "headroom": ceiling - dele,
            "worker_headroom": None if oracle is None else 1.0 - oracle,
            "capture": capture,
            "ceiling_is_oracle": oracle is not None,
        })

    tax = []
    for family, size in sizes:
        if family not in UNFAVOURABLE:
            continue
        solo = _get(table, system, "solo", family, size)
        dele = _get(table, system, cond, family, size)
        if solo is None or dele is None:
            continue
        tax.append({
            "family": family, "size": size, "solo": solo, "delegate": dele,
            "tax": solo - dele,
            "cost_ratio": _ratio(_get(table, system, cond, family, size, "total_tokens"),
                                 _get(table, system, "solo", family, size, "total_tokens")),
            "spawn_rate": _get(table, system, cond, family, size, "spawn_rate"),
        })

    runs = [r for r in records if r["system"] == system and r["condition"] == cond]
    decided = [(r["label"], bool(r["telemetry"].get("workers"))) for r in runs
               if r["label"] in ("delegate", "solo")]
    tpr = _avg([1.0 if spawned else 0.0 for label, spawned in decided if label == "delegate"])
    tnr = _avg([0.0 if spawned else 1.0 for label, spawned in decided if label == "solo"])
    process = [run_metrics(r) for r in runs if r["family"] in FAVOURABLE
               and r["telemetry"].get("workers")]
    # Capture skips cells where solo is already at the ceiling, so a delegate
    # that falls *below* solo there would vanish from it. Harm keeps it visible.
    harm = _avg([max(0.0, c["solo"] - c["delegate"]) for c in per_cell])
    return {
        "capture": (lift_sum / gap_sum) if gap_sum else None,
        "harm": harm,
        "cells": per_cell,
        "tax": tax,
        "mean_tax": _avg([t["tax"] for t in tax]),
        "mean_cost_ratio": _avg([t["cost_ratio"] for t in tax]),
        "decision_tpr": tpr,
        "decision_tnr": tnr,
        "decision_balanced_acc": None if tpr is None or tnr is None else (tpr + tnr) / 2,
        "coverage": _avg([p["coverage"] for p in process]),
        "duplication": _avg([p["duplication"] for p in process]),
        "synthesis_loss": _avg([p["synthesis_loss"] for p in process]),
        "mean_spawned": _avg([p["spawned"] for p in process]),
        "total_tokens": _avg([run_metrics(r)["total_tokens"] for r in runs]),
    }
