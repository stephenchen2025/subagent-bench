# lh31_assay_replicates: what completing it requires

Seed 1. Probes: the same procedure repeated on replicates that each differ, then an aggregate that is only right if every replicate's verdict is.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/replicates.json`.
- Grading: Per replicate: the verdict, and a valid run's concentration within 0.5 %. Summary: the number of valid runs exactly, their mean within 0.5 % and SD within 3 %. Reward = 0.7 x replicate accuracy + 0.3 x summary.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent replicate runs. For each one the agent must read the run's notes for reader, units, dilution and exclusions, drop excluded wells and saturated standards, fit the calibration, apply QC, and compute the concentration. That is about 5 turns and 1,400 tokens of reasoning and output per replicate run.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **52.4 min** |
| single agent, ideal (batches every read; floor) | **23.6 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.7 min** (peak 5,026 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 replicate runs (78,400 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Every replicate differs**: reader limits, standard units, dilution wording, excluded wells.
- **"50 uL sample + 950 uL buffer"** is a 20-fold dilution, not 19.
- **Saturated standards** above the reader's linear limit bend the fit if kept.
- **A superseded run** is named only in the LATER run that repeats it.
- **Average only the valid runs**: an invalid one in the mean moves it.

## Build and verify

```bash
docker build -t lh31_assay_replicates longhorizon/tasks/lh31_assay_replicates/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
