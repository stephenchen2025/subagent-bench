# lh29_fictional_calendars: what completing it requires

Seed 1. Probes: calendar and time-zone reasoning from written rules no library knows.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/runs.json`.
- Grading: Per job, all or nothing: its next three runs exactly right (UTC, to the minute). Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 50 independent jobs. For each one the agent must read the region's offset, summer-time rule, weekend and holidays, expand the job's schedule day by day from 26 September, and convert each run to UTC. That is about 5 turns and 1,500 tokens of reasoning and output per job.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **48.0 min** |
| single agent, ideal (batches every read; floor) | **22.5 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.7 min** (peak 5,375 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 50 jobs (75,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Invented regions**: no tz database applies; half-hour offsets.
- **Summer time** ends in October in some regions and starts in October in others.
- **Weekends differ**: Friday-Saturday, Thursday-Friday, Sunday-Monday.
- **Rule holidays** ("second Monday of October") and next-business-day roll-forwards.

## Build and verify

```bash
docker build -t lh29_fictional_calendars longhorizon/tasks/lh29_fictional_calendars/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
