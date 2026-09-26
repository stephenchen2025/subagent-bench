# lh17_flag_cleanup: what completing it requires

Seed 1. Probes: a per-unit policy decision followed by a behaviour-preserving refactor.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less` and `pytest`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: edited modules under `app/` and an updated `flags.yaml`.
- Grading: Per flag: a hidden behaviour test (removed flags: never consulted, final behaviour kept; kept flags: both states still work) passes, and flags.yaml lists it iff it should remain. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent flags. For each one the agent must read the flag's history, decide remove-on / remove-off / keep, then remove the check in whichever of five shapes it takes without changing behaviour. That is about 7 turns and 1,500 tokens of reasoning and output per flag.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **58.2 min** |
| single agent, ideal (batches every read; floor) | **21.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.2 min** (peak 7,848 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 flags (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Stale `status` labels**; the last history event decides.
- **The 30-day line** sits inside some histories.
- **Shapes**: `if not`, ternaries, helper functions, and `enabled(x) and order.get("beta")`, which must become the other condition, not `True`.
- **Kept flags must keep working both ways.**

## Build and verify

```bash
docker build -t lh17_flag_cleanup longhorizon/tasks/lh17_flag_cleanup/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
