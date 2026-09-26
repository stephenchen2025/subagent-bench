# lh22_reconciliation: what completing it requires

Seed 1. Probes: per-unit contract terms that change the arithmetic.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/recon.json`.
- Grading: Per merchant, all or nothing: all three lists exactly right. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 50 independent merchants. For each one the agent must read the merchant's contract, compute every expected payout (fee, FX order, refund rule, rounding, settlement mode), and diff against the bank lines. That is about 7 turns and 1,400 tokens of reasoning and output per merchant.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **58.6 min** |
| single agent, ideal (batches every read; floor) | **21.2 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **10.0 min** (peak 6,742 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 50 merchants (70,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **FX before or after the fee** gives different cents; so does the fixed fee in sale currency.
- **Refund fee rules differ.**
- **Batch merchants** settle daily sums; a batch short one sale is a bad batch, not an unsettled id.
- **Wrong-fee payouts** are off by cents, not missing.

## Build and verify

```bash
docker build -t lh22_reconciliation longhorizon/tasks/lh22_reconciliation/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
