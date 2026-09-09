#!/usr/bin/env python3
"""Run Milestone 1 for real: N models over the 30-task generated set.

    python tools/run_milestone1.py --models claude-opus-5,claude-sonnet-5

The thesis test (DESIGN.md 8.9): do models at matched task correctness separate
on decision yield? That needs at least two models over the same tasks, so
--models takes a comma list and the default is two rather than one.

Design choices that matter for a real run:

- **Resumable.** Every (model, task_id) episode is written to
  build/milestone1/episodes/<model>/<task_id>.json as soon as it completes. A
  second invocation skips whatever is already on disk, so an interrupted run
  costs nothing to restart -- rerun the same command.
- **Cost-guarded.** --max-cost-usd stops launching new episodes once mini's own
  running dollar total crosses it (checked between episodes, not mid-episode --
  mini has no client-side kill switch mid-response). Per-episode dollar cost
  is mini's own accounting (DESIGN.md 8.1 §3: token BUDGETS are ours and
  denominated in tokens; this is a wall on total spend, a different thing).
- **No container.** Harbor needs a sandbox this environment does not have,
  so this drives mini-swe-agent's LocalEnvironment directly, one task at a
  time, each in a fresh copy of its fixture. That means scope discipline runs
  on the host filesystem, not inside an image -- adequate for the thesis
  test, not a substitute for a real Harbor run before anything is published.
- **Noise-floor gated.** The frozen consumer cannot be made bit-deterministic
  (current Claude models reject temperature/top_p), so before comparison.md
  calls two models "separated" it measures how much a SINGLE model's judged
  yield moves on repeat judging of the same reports and refuses to call a gap
  real unless it clears that measured floor (DESIGN.md 7.1). Skippable with
  --noise-floor-sample 0 for a cheap first pass, at the cost of losing the only
  thing that tells a real gap from consumer noise.
"""

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

DEFAULT_MODELS = ["claude-opus-5", "claude-sonnet-5"]
STEP_LIMIT = 30
OUT = ROOT / "build" / "milestone1"


def _require_key():
    import os

    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit(
            "ANTHROPIC_API_KEY is not set. Set it in this project's environment\n"
            "config (not in a shell here, and never in a chat transcript); it is\n"
            "injected at container start, so a new session will have it."
        )


def _episode_path(model, task_id):
    safe_model = model.replace("/", "_")
    return OUT / "episodes" / safe_model / f"{task_id}.json"


def _load_specs():
    from tools.generate_tasks import build

    manifest, rejected = build(10, ROOT / "tasks" / "generated")
    if rejected:
        print(f"warning: {len(rejected)} variant(s) rejected by the behavioural gate")
    specs = {}
    for entry in manifest:
        path = ROOT / "tasks" / "generated" / "specs" / f"{entry['task_id']}.json"
        specs[entry["task_id"]] = json.loads(path.read_text())
    return specs


def run_one(model_name, spec, workdir):
    """Run one real episode. Returns (episode_dict, dollar_cost)."""
    from minisweagent.environments.local import LocalEnvironment
    from minisweagent.models import get_model

    from harness.agent import build_mini_agent
    from harness.episode_runner import run_episode

    repo = workdir / "repo"
    shutil.copytree(ROOT / spec["env"]["snapshot"] / "repo", repo)

    model = get_model(model_name)
    agent = build_mini_agent(model, LocalEnvironment(cwd=str(repo)), step_limit=STEP_LIMIT)
    budget = spec["budget"]["max_tokens"]

    episode, handback_result = run_episode(
        agent, spec, lambda text: max(1, len(text) // 4),
        logs_dir=workdir / "logs",
        start=lambda: agent.run(task=spec["brief"], budget_tokens=budget),
    )
    record = {
        "task_id": episode.task_id,
        "family": episode.family,
        "model": model_name,
        "report": episode.report,
        "trajectory": episode.trajectory,
        "effects": episode.effects,
        "usage": {
            "input_tokens": episode.usage.input_tokens,
            "output_tokens": episode.usage.output_tokens,
            "tool_calls": episode.usage.tool_calls,
        },
        "budget_tokens": episode.budget_tokens,
        "reference_tokens": episode.reference_tokens,
        "tokens_exact": getattr(episode, "tokens_exact", False),
        "handback": None if handback_result is None else {
            "pushback": handback_result.pushback,
            "first_report": handback_result.first_report,
            "final_report": handback_result.final_report,
            "report_changed": handback_result.report_changed,
        },
        "mini_cost_usd": getattr(agent, "cost", 0.0),
    }
    return record, getattr(agent, "cost", 0.0)


def score_all(models, consumer=None, specs=None):
    """Score every completed episode with the frozen consumer.

    `consumer` and `specs` are injectable so orchestration (resumability,
    aggregation, the comparison writer) can be tested without an API key or a
    generated task set on disk; both default to the real ones for an actual
    run -- the live consumer, and specs loaded from tasks/generated/specs.
    """
    from scorers.aggregate import score_episode, scorecard
    from scorers.episode import Episode, Usage

    per_model = {}
    for model in models:
        model_dir = OUT / "episodes" / model.replace("/", "_")
        if not model_dir.exists() or not any(model_dir.glob("*.json")):
            continue
        if consumer is None:
            # Constructed lazily and once: nothing to score should never require
            # network or `anthropic` to be installed.
            from consumer.claude import ClaudeConsumer

            consumer = ClaudeConsumer()
        rows = []
        for path in sorted(model_dir.glob("*.json")):
            record = json.loads(path.read_text())
            if specs is not None:
                spec = specs[record["task_id"]]
            else:
                spec = json.loads(
                    (ROOT / "tasks" / "generated" / "specs" /
                     f"{record['task_id']}.json").read_text()
                )
            episode = Episode(
                task_id=record["task_id"], family=record["family"],
                report=record["handback"]["final_report"] if record["handback"] else record["report"],
                trajectory=record["trajectory"], effects=record["effects"],
                usage=Usage(**record["usage"]),
                budget_tokens=record["budget_tokens"],
                reference_tokens=record["reference_tokens"],
            )
            rows.append(score_episode(episode, spec, consumer))
        if rows:
            per_model[model] = scorecard(rows, budgets=tuple({r["budget_tokens"] for r in rows}))
    return per_model


def main(argv=None, run_one_fn=run_one, consumer=None, out_dir=None, require_key=True,
         noise_floor_fn=None):
    """`run_one_fn`, `consumer`, `out_dir`, `require_key` and `noise_floor_fn` are
    injectable so this whole orchestration -- resumability, the cost cap,
    scoring, the noise floor, the comparison writer -- can be exercised in
    tests with no network and no key. A real invocation uses every default."""
    global OUT
    if out_dir is not None:
        OUT = Path(out_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument("--models", default=",".join(DEFAULT_MODELS))
    parser.add_argument("--max-cost-usd", type=float, default=20.0)
    parser.add_argument("--score-only", action="store_true",
                        help="Skip running episodes; score whatever is already on disk.")
    parser.add_argument("--noise-floor-sample", type=int, default=3,
                        help="Episodes per model to re-judge for the noise floor. "
                             "0 disables it (DESIGN.md 7.1 -- not recommended).")
    parser.add_argument("--noise-floor-repeats", type=int, default=3,
                        help="Re-judgments per sampled episode.")
    args = parser.parse_args(argv)
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    specs_for_scoring = None
    if not args.score_only:
        if require_key:
            _require_key()
        specs = _load_specs()
        specs_for_scoring = specs
        OUT.mkdir(parents=True, exist_ok=True)
        total_cost = 0.0
        planned = [(m, tid) for m in models for tid in specs]
        skipped = sum(1 for m, tid in planned if _episode_path(m, tid).exists())
        print(f"{len(planned)} episode(s) planned, {skipped} already on disk, "
              f"cost cap ${args.max_cost_usd:.2f}\n")

        for model, task_id in planned:
            out_path = _episode_path(model, task_id)
            if out_path.exists():
                continue
            if total_cost >= args.max_cost_usd:
                print(f"\nStopped: mini's running cost ${total_cost:.2f} reached the "
                      f"${args.max_cost_usd:.2f} cap. Re-run this command to resume; "
                      "completed episodes are skipped.")
                break
            spec = specs[task_id]
            print(f"  {model:20} {task_id:28} ", end="", flush=True)
            t0 = time.time()
            with tempfile.TemporaryDirectory(prefix="handoff-m1-") as tmp:
                try:
                    record, cost = run_one_fn(model, spec, Path(tmp))
                except Exception as exc:  # noqa: BLE001 - one bad episode must not sink the run
                    print(f"FAILED ({exc})")
                    continue
            total_cost += cost
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(record, indent=2))
            print(f"${cost:.3f}  {time.time() - t0:.0f}s  "
                  f"report={'yes' if record['report'].strip() else 'NO'}")

        print(f"\nmini spend this run: ${total_cost:.2f}")

    if specs_for_scoring is None:
        try:
            specs_for_scoring = _load_specs()
        except Exception:  # noqa: BLE001 - fall back to score_all's own disk lookup
            specs_for_scoring = None

    # Built once, before scoring, and shared with the noise-floor step below --
    # both must judge with the literal same consumer instance, or a difference
    # between them would confound "the model changed" with "the consumer did".
    if consumer is None and any(
        (OUT / "episodes" / m.replace("/", "_")).exists() for m in models
    ):
        from consumer.claude import ClaudeConsumer

        consumer = ClaudeConsumer()

    print("\nScoring...")
    per_model = score_all(models, consumer=consumer, specs=specs_for_scoring)
    from report.render import markdown

    noise_floors = {}
    if args.noise_floor_sample > 0 and consumer is not None:
        # Resolved here, not as a default argument value, because
        # measure_noise_floor is defined later in this file.
        noise_floor_fn = noise_floor_fn or measure_noise_floor
        for model in per_model:
            noise_floors[model] = noise_floor_fn(
                model, consumer, specs_for_scoring or {},
                sample_size=args.noise_floor_sample, repeats=args.noise_floor_repeats,
            )

    for model, card in per_model.items():
        floor = noise_floors.get(model)
        floor_note = (
            f" Noise floor: sampled {floor['sampled']}, mean spread {floor['mean_spread']:.3f}."
            if floor else " Noise floor not measured."
        )
        note = (f"Milestone 1 -- real model ({model}), real frozen consumer, "
                f"generated tasks.{floor_note}")
        (OUT / f"{model.replace('/', '_')}.md").write_text(
            markdown(card, title=f"HANDOFF Milestone 1 -- {model}", note=note)
        )
        dy = card["dy_at_budget"]
        print(f"  {model:20} yield {card['decision_yield']:.2f}  "
              f"AUROC {card['calibration']['auroc']}  "
              + "  ".join(f"{k}={v}" for k, v in dy.items())
              + (f"  noise-floor={floor['mean_spread']:.3f}" if floor else ""))

    if len(per_model) >= 2:
        _write_comparison(per_model, out_dir=OUT, noise_floors=noise_floors)
    print(f"\nreports in {OUT}")
    return per_model


def measure_noise_floor(model, consumer, specs, sample_size=3, repeats=3, seed=0):
    """How much this model's judged yield moves on repeat judging alone.

    Samples up to `sample_size` of the model's own completed episodes and
    re-judges each `repeats` times with the SAME consumer and SAME report --
    the only thing that can vary is the consumer's own non-determinism. Returns
    None if there is nothing on disk to sample, which callers must treat as
    "unmeasured", not "zero".
    """
    import random

    from consumer.base import noise_floor
    from consumer.probe import Probe

    model_dir = OUT / "episodes" / model.replace("/", "_")
    paths = sorted(model_dir.glob("*.json")) if model_dir.exists() else []
    if not paths or sample_size <= 0:
        return None

    rng = random.Random(seed)
    sample = rng.sample(paths, min(sample_size, len(paths)))
    floors = []
    for path in sample:
        record = json.loads(path.read_text())
        spec = specs.get(record["task_id"]) if specs else None
        if spec is None:
            continue
        probes = [Probe.from_spec(p) for p in spec["decision_probe"]]
        report = (
            record["handback"]["final_report"] if record["handback"] else record["report"]
        )
        floors.append(noise_floor(consumer, report, probes, repeats=repeats))

    if not floors:
        return None
    return {
        "sampled": len(floors),
        "repeats": repeats,
        "mean_spread": sum(f["decision_yield_spread"] for f in floors) / len(floors),
        "max_spread": max(f["decision_yield_spread"] for f in floors),
        "per_episode": floors,
    }


def _write_comparison(per_model, out_dir=None, noise_floors=None):
    """The thesis check itself: do models separate on decision yield?"""
    out_dir = out_dir if out_dir is not None else OUT
    lines = ["# Milestone 1 -- model comparison", "",
            "The falsification test (DESIGN.md 8.9): if models with matched task "
            "correctness do not separate on decision yield, the design is wrong.",
            "", "| model | decision yield | CIR yield | false certainty | AUROC |",
            "|---|---|---|---|---|"]
    for model, card in per_model.items():
        cal = card["calibration"]["auroc"]
        lines.append(
            f"| {model} | {card['decision_yield']:.3f} | {card['cir_yield']} | "
            f"{card['false_certainty']} | {cal if cal is None else f'{cal:.3f}'} |"
        )
    noise_floors = noise_floors or {}
    if noise_floors:
        lines += ["", "## Noise floor", "",
                  "Measured by re-judging each model's own reports with the same "
                  "consumer, holding the report fixed (DESIGN.md 7.1). A yield gap "
                  "smaller than this is not attributable to the report -- it is "
                  "consumer noise.", "",
                  "| model | sampled | repeats | mean spread |", "|---|---|---|---|"]
        for model, floor in noise_floors.items():
            if floor is None:
                lines.append(f"| {model} | - | - | unmeasured |")
            else:
                lines.append(
                    f"| {model} | {floor['sampled']} | {floor['repeats']} | "
                    f"{floor['mean_spread']:.3f} |"
                )
        lines.append("")

    yields = {m: c["decision_yield"] for m, c in per_model.items() if c["decision_yield"] is not None}
    if len(yields) >= 2:
        gap = max(yields.values()) - min(yields.values())
        measured = [f["mean_spread"] for f in noise_floors.values() if f is not None]
        if measured:
            floor = max(measured)
            verdict = (
                "**Models did not separate: the yield gap "
                f"({gap:.3f}) does not clear the measured noise floor ({floor:.3f}).**"
                if gap <= floor else
                f"Yield gap ({gap:.3f}) clears the measured noise floor ({floor:.3f})."
            )
        else:
            floor = 0.05
            verdict = (
                "**Models did not separate on decision yield at this sample size "
                f"(gap {gap:.3f} < {floor:.2f}). Noise floor was not measured -- this "
                "is a fallback threshold, not a measured one.**"
                if gap < floor else
                f"Yield gap ({gap:.3f}) exceeds the fallback threshold ({floor:.2f}); "
                "noise floor was not measured, so treat this as provisional."
            )
        if "did not separate" in verdict:
            lines += ["", verdict, "",
                     "Per DESIGN.md 8.9, failing to separate is the signal to stop and "
                     "revisit the design before authoring more tasks -- not a result to "
                     "average past."]
        else:
            lines += ["", verdict]
    (out_dir / "comparison.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
