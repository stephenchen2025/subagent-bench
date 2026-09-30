# lh34_transit_vetting: what completing it requires

Seed 1. Probes: per-object physical reasoning where the data hide what the obvious calculation assumes.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/vetting.json`.
- Grading: Per star, all or nothing: the class; for a planet, period within 0.1 % and radius within 2 %. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 52 independent stars. For each one the agent must drop low-SNR dips, find the orbit numbers across the gaps, refine the period, correct depths for contaminating light, compare odd and even eclipses, and convert depth to a radius. That is about 5 turns and 1,400 tokens of reasoning and output per star.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **49.2 min** |
| single agent, ideal (batches every read; floor) | **22.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.6 min** (peak 6,291 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 52 stars (72,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Missed transits**: dips are not consecutive orbits, so (last - first) / (count - 1) is wrong.
- **Low-SNR dips** that break the period if kept.
- **Dilution** by a neighbouring star makes eclipses look shallower -- and can turn a planet into an EB.
- **Odd/even depths** that differ reveal an eclipsing binary.
- **Stellar radius in km** for some stars.

## Build and verify

```bash
docker build -t lh34_transit_vetting longhorizon/tasks/lh34_transit_vetting/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
