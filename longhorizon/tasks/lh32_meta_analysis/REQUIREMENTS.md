# lh32_meta_analysis: what completing it requires

Seed 1. Probes: eligibility judgements and extraction per report, then a pooled estimate only right if every report's decision is.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/review.json`.
- Grading: Per report: the include decision, and for an included trial log RR within 0.005 and SE within 1 %. Pooled: k, RR and CI. Reward = 0.7 x report accuracy + 0.3 x pooled.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent trial reports. For each one the agent must check design, population, comparator and the week-12 outcome, match the registration number against other reports, read events from the week-12 row, use the randomised denominators, and compute log RR and SE. That is about 5 turns and 1,400 tokens of reasoning and output per trial report.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.0 min** |
| single agent, ideal (batches every read; floor) | **23.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.7 min** (peak 5,940 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 trial reports (78,400 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **"Non-randomised"** contains "randomised".
- **Duplicates** share a registration number; keep the report with more randomised.
- **Intention to treat**: the denominator is randomised, not completers.
- **Percentages** of those randomised must be turned back into counts.
- **Arm order** varies; **zero cells** need the 0.5 correction.

## Build and verify

```bash
docker build -t lh32_meta_analysis longhorizon/tasks/lh32_meta_analysis/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
