# lh30_spec_validators: what completing it requires

Seed 1. Probes: implementing a precise written specification, graded on unseen near misses.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `validators/<format>.py` with `is_valid(text)` for every format.
- Grading: Per format, all or nothing: every hidden string (valid ones and near misses) classified correctly. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent identifier formats. For each one the agent must read the spec's structure, alphabet and check algorithm with its parameters, implement it, and test it on the examples and on near misses you construct. That is about 6 turns and 1,600 tokens of reasoning and output per identifier format.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.3 min** |
| single agent, ideal (batches every read; floor) | **23.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.5 min** (peak 5,374 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 identifier formats (76,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Per-format parameters**: weights, what a check value of 10 becomes, pivot years, separators.
- **Real dates only**: 30 February and month 13 are invalid; leap years matter.
- **Reserved and forbidden letters.**
- **Separators only where allowed**; a regex that strips all hyphens accepts near misses.
- **Upper case is part of the format.**

## Build and verify

```bash
docker build -t lh30_spec_validators longhorizon/tasks/lh30_spec_validators/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
