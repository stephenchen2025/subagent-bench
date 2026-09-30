# lh26_expense_audit: what completing it requires

Seed 1. Probes: applying an ordered rulebook exactly, with lookups and currency arithmetic per line.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/expenses.json`.
- Grading: Per report: 0.5 for the reimbursable amount to the cent, 0.5 for the exact set of broken rules. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent expense reports. For each one the agent must walk every line through the ordered rules (FX at the line's date, receipts, alcohol, weekends, hotel caps, flight class), then apply daily meal caps, and total. That is about 6 turns and 1,500 tokens of reasoning and output per expense report.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **60.9 min** |
| single agent, ideal (batches every read; floor) | **25.3 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.6 min** (peak 6,844 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 expense reports (84,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Order matters**: receipts are judged on the converted amount; meal caps apply after deductions.
- **Weekend meals** are fine on the first and last day.
- **Business class** needs both >6 hours and an approval id.
- **FX per line date**, not the trip start.

## Build and verify

```bash
docker build -t lh26_expense_audit longhorizon/tasks/lh26_expense_audit/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
