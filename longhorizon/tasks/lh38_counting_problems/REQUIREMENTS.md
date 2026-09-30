# lh38_counting_problems: what completing it requires

Seed 1. Probes: exact answers where one misread word (round, at least, with replacement) changes the count.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/answers.json`.
- Grading: Per problem, all or nothing: both parts exactly. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent problems. For each one the agent must model the problem precisely -- what is distinguishable, what is ordered, which bound is inclusive -- count it, and check the count a second way. That is about 5 turns and 1,400 tokens of reasoning and output per problem.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.1 min** |
| single agent, ideal (batches every read; floor) | **23.8 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.7 min** (peak 5,910 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 problems (78,400 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Round tables**: rotations are the same seating.
- **Repeated letters** are indistinguishable.
- **At least / at most / exactly** and inclusive bounds.
- **With vs without replacement.**
- **Constraints on single variables** (upper bounds) in stars-and-bars problems.

## Build and verify

```bash
docker build -t lh38_counting_problems longhorizon/tasks/lh38_counting_problems/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
