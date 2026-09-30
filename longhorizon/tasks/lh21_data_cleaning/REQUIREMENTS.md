# lh21_data_cleaning: what completing it requires

Seed 1. Probes: following a per-unit written procedure exactly, where step order and parameters differ.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `clean/<name>.csv` for 46 datasets.
- Grading: Per dataset: exact header required; then the longest in-order run of exactly matching rows over the larger of expected and submitted counts. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 46 independent datasets. For each one the agent must read the dataset's spec, implement its steps in its order with its parameters, and check the output against the raw rows. That is about 7 turns and 1,600 tokens of reasoning and output per dataset.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **59.6 min** |
| single agent, ideal (batches every read; floor) | **22.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.2 min** (peak 11,266 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 46 datasets (73,600 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Step order.** De-duplicating before the key is trimmed and upper-cased keeps different rows than after.
- **Parameters differ per dataset**: country code, date format, money notation, synonyms, sort keys.
- **Name particles** (van der, de, da) belong to the last name.
- **Dropping rules**: bad dates, unknown enum values and invalid emails remove the row; short phones only blank the field.

## Build and verify

```bash
docker build -t lh21_data_cleaning longhorizon/tasks/lh21_data_cleaning/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
