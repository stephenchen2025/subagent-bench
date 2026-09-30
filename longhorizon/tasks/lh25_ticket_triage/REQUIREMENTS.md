# lh25_ticket_triage: what completing it requires

Seed 1. Probes: multi-source judgement per item: content, customer record, policy matrix, knowledge base, history.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/triage.json`.
- Grading: Per ticket, all five fields right. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 80 independent tickets. For each one the agent must classify the problem by what the customer experiences, look up the plan, apply the matrix, pick the matching KB article, check the refund threshold and the customer's recent tickets. That is about 4 turns and 900 tokens of reasoning and output per ticket.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **57.9 min** |
| single agent, ideal (batches every read; floor) | **23.0 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.6 min** (peak 9,712 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 80 tickets (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Keywords mislead**: a 2FA how-to mentions security.
- **Plans are only in accounts.csv.**
- **Refund thresholds** after currency conversion.
- **48 hours**: a follow-up 49 hours later is a new ticket, not a duplicate.
- **KB matches by symptom**, and some problems have no article.

## Build and verify

```bash
docker build -t lh25_ticket_triage longhorizon/tasks/lh25_ticket_triage/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
