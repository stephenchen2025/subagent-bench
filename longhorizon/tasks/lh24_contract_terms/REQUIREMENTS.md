# lh24_contract_terms: what completing it requires

Seed 1. Probes: reading legal prose precisely, where amendments override and values need computing.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/contracts.json`.
- Grading: Per contract: the fraction of seven fields exactly right. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent contracts. For each one the agent must read the agreement and its amendments in order, normalise words and dates, and compute notice days, the next renewal date and the liability cap. That is about 6 turns and 1,300 tokens of reasoning and output per contract.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **59.9 min** |
| single agent, ideal (batches every read; floor) | **22.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.2 min** (peak 9,174 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 contracts (72,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Amendments override**, and a later one can override an earlier one.
- **Numbers as words** and three date formats.
- **Notice in months** is 30 days each.
- **Renewal periods can differ** from the initial term.
- **Fee-based caps** are twelve monthly fees at the contract's own USD rate.

## Build and verify

```bash
docker build -t lh24_contract_terms longhorizon/tasks/lh24_contract_terms/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
