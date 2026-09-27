# lh23_experiment_audit: what completing it requires

Seed 1. Probes: statistical judgement under a fixed protocol, where the write-up is not to be trusted.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/verdicts.json`.
- Grading: Per experiment, the verdict. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 50 independent experiments. For each one the agent must read the pre-registration and the claim, exclude bots, run the SRM check against the registered split, check sample sizes, compare metrics, and run the corrected z-test. That is about 7 turns and 1,400 tokens of reasoning and output per experiment.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **61.2 min** |
| single agent, ideal (batches every read; floor) | **21.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **10.0 min** (peak 10,760 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 50 experiments (70,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Bots** push arms over the minimum until they are excluded.
- **A 90/10 split** is unbalanced by design; testing it against 50/50 finds a false SRM.
- **Three arms** halve the threshold.
- **Reported p-values** are always under 0.05; recompute.
- **Check order matters**: an SRM experiment is `srm` even if its metric is also wrong.

## Build and verify

```bash
docker build -t lh23_experiment_audit longhorizon/tasks/lh23_experiment_audit/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
