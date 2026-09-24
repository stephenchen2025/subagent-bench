#!/usr/bin/env python3
"""Orchestrator-track verifier. Runs inside the task container, stdlib only.

Harbor uploads tests/ to /tests only after the agent has finished, so the ground
truth never shares a filesystem with the agent. This script reads it, grades the
workspace, and writes /logs/verifier/reward.json:

    {"reward": <0..1>, <sub-score>: <number>, ...}

`reward` is the task score every orchestrator metric is built from
(ORCHESTRATOR.md 5). It is graded, not pass/fail: a delegate run that finds 15 of
18 duplicate charges should score differently from one that finds 3.

Paths are overridable so the same file grades local, containerless runs.
"""

import importlib.util
import json
import os
import shutil
import sys

WORKSPACE = os.environ.get("ORCH_WORKSPACE", "/workspace")
TESTS = os.environ.get("ORCH_TESTS", os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("ORCH_REWARD_DIR", "/logs/verifier")


def _load_answer():
    path = os.path.join(WORKSPACE, "answer.json")
    try:
        with open(path) as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _f1(tp, n_pred, n_true):
    precision = tp / n_pred if n_pred else 0.0
    recall = tp / n_true if n_true else 1.0
    if precision + recall == 0:
        return precision, recall, 0.0
    return precision, recall, 2 * precision * recall / (precision + recall)


def grade_wide(truth):
    answer = _load_answer() or {}
    raw = answer.get("matches", [])
    predicted = {}
    for item in raw if isinstance(raw, list) else []:
        if isinstance(item, dict) and isinstance(item.get("ticket"), str):
            predicted[item["ticket"].strip()] = str(item.get("order", "")).strip()
    expected = {m["ticket"]: m["order"] for m in truth["matches"]}
    pair_tp = sum(1 for t, o in predicted.items() if expected.get(t) == o)
    ticket_tp = sum(1 for t in predicted if t in expected)
    p, r, f1 = _f1(pair_tp, len(predicted), len(expected))
    _, _, ticket_f1 = _f1(ticket_tp, len(predicted), len(expected))
    return {
        "reward": round(f1, 4),
        "precision": round(p, 4),
        "recall": round(r, 4),
        "ticket_f1": round(ticket_f1, 4),
        "answer_present": int(bool(answer)),
    }


def grade_probe(truth):
    answer = _load_answer() or {}
    got = answer.get("services", {})
    got = got if isinstance(got, dict) else {}
    expected = truth["services"]
    component = cause = 0
    for svc, want in expected.items():
        item = got.get(svc) or {}
        if not isinstance(item, dict):
            continue
        component += str(item.get("component", "")).strip() == want["component"]
        cause += str(item.get("cause", "")).strip() == want["cause"]
    n = len(expected)
    return {
        "reward": round((component + cause) / (2 * n), 4),
        "component_acc": round(component / n, 4),
        "cause_acc": round(cause / n, 4),
        "answer_present": int(bool(answer)),
    }


def grade_chain(truth):
    """Correct prefix of the visited path, over the chain's length."""
    answer = _load_answer() or {}
    path = answer.get("path", [])
    path = [str(p).strip() for p in path] if isinstance(path, list) else []
    expected = truth["path"]
    prefix = 0
    for got, want in zip(path, expected):
        if got != want:
            break
        prefix += 1
    return {
        "reward": round(prefix / len(expected), 4),
        "hops_correct": prefix,
        "closing_code": int(str(answer.get("closing_code", "")).strip() == truth["closing_code"]),
        "answer_present": int(bool(answer)),
    }


def run_checks(truth):
    """Import the hidden checks with the workspace importable; one point each."""
    sys.path.insert(0, WORKSPACE)
    spec = importlib.util.spec_from_file_location(
        "hidden_checks", os.path.join(TESTS, "hidden_checks.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = {}
    for name in truth["checks"]:
        try:
            getattr(module, name)()
            results[name] = 1
        except Exception:  # noqa: BLE001 -- any failure in agent code is a failed check
            results[name] = 0
    passed = sum(results.values())
    return {"reward": round(passed / len(results), 4), **results}


GRADERS = {"W": grade_wide, "P": grade_probe, "C": run_checks, "L": grade_chain}


def main():
    with open(os.path.join(TESTS, "ground_truth.json")) as fh:
        truth = json.load(fh)
    family = truth["family"]
    os.environ.setdefault("ORCH_WORKSPACE", WORKSPACE)
    try:
        rewards = GRADERS[family](truth)
    except Exception as exc:  # noqa: BLE001 -- a crashed grader is a zero, not a crash
        print(f"verifier error: {exc!r}", file=sys.stderr)
        rewards = {"reward": 0.0, "verifier_error": 1}
    os.makedirs(OUT, exist_ok=True)
    # Harbor downloads the verifier dir, not the workspace. The final answer
    # rides along so synthesis loss can be scored offline (ORCHESTRATOR.md 5.3).
    answer = os.path.join(WORKSPACE, "answer.json")
    if os.path.isfile(answer):
        shutil.copy(answer, os.path.join(OUT, "answer.json"))
    with open(os.path.join(OUT, "reward.json"), "w") as fh:
        json.dump(rewards, fh)
    print(json.dumps(rewards))
    return rewards


if __name__ == "__main__":
    main()
