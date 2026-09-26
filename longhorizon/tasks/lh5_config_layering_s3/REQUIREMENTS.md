# lh5_config_layering_s3: what completing it requires

Family `lh5_config_layering`, seed 3. Probes: precedence rules applied across many units (F1: the brief leaves them to the docs).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/effective.json`.
- Grading: Per service: five items (four effective values and the violations set). Reward is the mean fraction.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 64 independent services. For each one the agent must find the service's env prefix, read base.yaml, the prod overlay and prod.env, apply precedence and unit rules, and check limits. That is about 5 turns and 1,200 tokens of reasoning and output per service.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **58.0 min** |
| single agent, ideal (batches every read; floor) | **23.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.6 min** (peak 7,803 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 64 services (76,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **The EU overlay does not apply to prod.**
- **Commented-out** env lines, **deprecated** blocks, and variables with **another prefix** are not overrides.
- **`_MS` variables** are milliseconds.

## Build and verify

```bash
docker build -t lh5_config_layering_s3 longhorizon/tasks/lh5_config_layering_s3/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
