# lh39_ecology_surveys: what completing it requires

Seed 1. Probes: a fixed procedure applied to data that each observer's notes quietly amend.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/diversity.json`.
- Grading: Per plot, all or nothing: validity; exact richness; Shannon and Simpson within 0.001; density within 0.5 %. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 54 independent plots. For each one the agent must merge synonym codes, apply the notes' re-identifications, double counts and late vials, drop spiders, ants and unidentified specimens, check the sampling effort, and compute the four metrics. That is about 5 turns and 1,400 tokens of reasoning and output per plot.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **50.8 min** |
| single agent, ideal (batches every read; floor) | **22.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.6 min** (peak 5,654 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 54 plots (75,600 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Synonym codes** split one species' count across two rows.
- **Re-identifications** move individuals between species; a confirmation note changes nothing.
- **Non-target taxa** (spiders, ants, UNK) sit in the same tally.
- **Area** in m^2, hectares, or as length x width.
- **Natural log** for Shannon; Simpson with n(n-1), not p^2.

## Build and verify

```bash
docker build -t lh39_ecology_surveys longhorizon/tasks/lh39_ecology_surveys/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
