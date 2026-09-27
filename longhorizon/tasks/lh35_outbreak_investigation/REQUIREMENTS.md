# lh35_outbreak_investigation: what completing it requires

Seed 1. Probes: a case definition applied to free-text answers, then an analysis that one misclassified person moves.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/outbreaks.json`.
- Grading: Per event, all or nothing: the number of cases, the vehicle, and its risk ratio within 1 %. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent outbreaks. For each one the agent must classify every attendee by symptoms and onset window, build a 2x2 table per food leaving out blanks and excluded people, and pick the vehicle by risk ratio among foods most cases ate. That is about 5 turns and 1,400 tokens of reasoning and output per outbreak.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **47.2 min** |
| single agent, ideal (batches every read; floor) | **20.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **7.6 min** (peak 10,244 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 outbreaks (67,200 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Symptoms in free text**: "the runs", "being sick" count; nausea alone does not.
- **The onset window**: ill 5 hours after the meal, or on day four, is excluded, not a case.
- **Blank answers** leave a person out of that food's table only.
- **Household contacts** who were not at the meal (attended = N) fall ill later and must be excluded.
- **Zero cells** need the 0.5 correction.

## Build and verify

```bash
docker build -t lh35_outbreak_investigation longhorizon/tasks/lh35_outbreak_investigation/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
