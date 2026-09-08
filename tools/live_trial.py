#!/usr/bin/env python3
"""Run ONE real trial: a live model on a real fixture, scored by the live consumer.

    python tools/live_trial.py [task_id]

This is the cheapest way to learn the things only a real call can teach -- does a
model follow the report contract, what does a trajectory actually cost, and what
is the consumer's noise floor. It deliberately needs neither Docker nor Harbor:
mini-swe-agent's LocalEnvironment runs the agent in a subprocess against a COPY
of the fixture, so the only prerequisite is ANTHROPIC_API_KEY.

A real container is still required for a real benchmark run -- LocalEnvironment
is not a sandbox, and the tool surface is the host's, not the image's (DESIGN.md
8.1). This is a wiring check, not a result.
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODEL = "claude-opus-5"
STEP_LIMIT = 25


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set.\n"
            "Set it in this project's environment config (not in a shell here, and\n"
            "never in a chat transcript); it is injected at container start, so a\n"
            "new session will have it."
        )

    task_id = sys.argv[1] if len(sys.argv) > 1 else "f2_retry_config_ghost"
    spec = next(
        json.loads(p.read_text())
        for p in sorted((ROOT / "tasks/examples").glob("*.json"))
        if json.loads(p.read_text())["id"] == task_id
    )

    from minisweagent.environments.local import LocalEnvironment
    from minisweagent.models import get_model

    from consumer.claude import ClaudeConsumer
    from consumer.base import noise_floor
    from consumer.probe import Probe
    from harness.agent import build_mini_agent
    from harness.episode_runner import missing_report, run_episode
    from scorers.aggregate import render, score_episode, scorecard

    workspace = Path(tempfile.mkdtemp(prefix="handoff-"))
    shutil.copytree(ROOT / spec["env"]["snapshot"] / "repo", workspace / "repo")
    cwd = str(workspace / "repo")
    print(f"task      {task_id}\nworkspace {cwd}\nmodel     {MODEL}\n")

    agent = build_mini_agent(
        get_model(MODEL), LocalEnvironment(cwd=cwd), step_limit=STEP_LIMIT
    )
    budget = spec["budget"]["max_tokens"]
    episode, hb = run_episode(
        agent, spec, lambda text: max(1, len(text) // 4),
        logs_dir=workspace / "logs",
        start=lambda: agent.run(task=spec["brief"], budget_tokens=budget),
    )

    print("--- report " + "-" * 56)
    print(episode.report or "(no delimited report -- the contract was not followed)")
    print("-" * 67)
    print(f"steps {episode.usage.tool_calls}  trajectory {len(episode.trajectory)}  "
          f"mini cost ${getattr(agent, 'cost', 0):.4f}")
    if missing_report(episode):
        print("\nThe agent produced no delimited report. That is a finding about the "
              "report contract, not a crash -- see harness/templates.py.")

    consumer = ClaudeConsumer()
    row = score_episode(episode, spec, consumer)
    print("\n--- scorecard " + "-" * 53)
    print(render(scorecard([row], budgets=(budget,))))

    probes = [Probe.from_spec(p) for p in spec["decision_probe"]]
    print("\n--- consumer noise floor (5 repeats) " + "-" * 30)
    floor = noise_floor(consumer, episode.report, probes, repeats=5)
    print(f"mean yield {floor['decision_yield_mean']:.3f}  "
          f"spread {floor['decision_yield_spread']:.3f}")
    for probe in floor["per_probe"]:
        print(f"  agreement {probe['agreement']:.2f}  {probe['question'][:52]}")
    print("\nDifferences below that spread are ties, not results (DESIGN.md 7.1).")


if __name__ == "__main__":
    main()
