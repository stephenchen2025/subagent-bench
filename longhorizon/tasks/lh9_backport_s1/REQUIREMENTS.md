# lh9_backport_s1: what completing it requires

Family `lh9_backport`, seed 1. Probes: code that moved between versions (F4); genuine negatives (F3); a frozen constraint.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less` and `pytest`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: patched release lines under `/workspace/releases/` and `BACKPORT_REPORT.md`.
- Grading: Per line: supported and affected lines must pass a hidden exploit test and their own tests; unaffected lines must be unchanged. Reward is the mean -- and **0 if any end-of-life line was modified**.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 32 independent release lines. For each one the agent must find where this line joins paths (four code shapes, era boundaries vary by seed), decide whether it is affected, adapt the fix, and run its tests. That is about 9 turns and 2,500 tokens of reasoning and output per release line.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **58.0 min** |
| single agent, ideal (batches every read; floor) | **24.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.6 min** (peak 16,186 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 32 release lines (80,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **The patch does not apply** anywhere but 4.x; every era keeps the logic elsewhere.
- **Not affected** lines (predating the helper, or already safe) must stay unchanged.
- **End-of-life lines are frozen**, scattered rather than a range.

## Build and verify

```bash
docker build -t lh9_backport_s1 longhorizon/tasks/lh9_backport_s1/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
