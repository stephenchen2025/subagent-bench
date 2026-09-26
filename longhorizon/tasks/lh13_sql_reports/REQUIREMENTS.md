# lh13_sql_reports: what completing it requires

Seed 1. Probes: business definitions a literal query gets wrong; graded on unseen data.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: one SELECT per question in `answers/QNN.sql`.
- Grading: Per question: the query, run on a hidden warehouse with the same schema and different rows, must return the oracle's rows. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent questions. For each one the agent must translate the question through DEFINITIONS.md (Berlin days, FX per UTC day, refunds, statuses, deleted customers, discontinued SKUs) into one query and check it on the visible data. That is about 6 turns and 1,600 tokens of reasoning and output per question.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.1 min** |
| single agent, ideal (batches every read; floor) | **23.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.5 min** (peak 5,244 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 questions (76,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Berlin, not UTC.** Orders near UTC midnight land on the next Berlin day, and the offset changes on 29 March.
- **FX per day** for orders, and per refund day for refunds.
- **Status semantics.** `refunded` is not revenue but is in the refund-rate denominator.
- **Deleted customers** drop out of customer counts but not out of revenue or rankings.
- **Hidden data.** A query that hardcodes a number computed on the visible copy scores zero.

## Build and verify

```bash
docker build -t lh13_sql_reports longhorizon/tasks/lh13_sql_reports/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
