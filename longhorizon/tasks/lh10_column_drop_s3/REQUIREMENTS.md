# lh10_column_drop_s3: what completing it requires

Family `lh10_column_drop`, seed 3. Probes: genuine negatives (F3); name collisions and dead mentions (F4).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/columns.json`.
- Grading: Per column: the verdict, and for `unsafe` a real production location within 3 lines. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 64 independent columns. For each one the agent must search the whole repo and config for the column, and judge every hit: which table, whether it is production, whether it is a read. That is about 6 turns and 1,200 tokens of reasoning and output per column.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **69.5 min** |
| single agent, ideal (batches every read; floor) | **24.5 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **10.5 min** (peak 14,154 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 64 columns (76,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Name collisions**: `status` exists on several tables.
- **Dead mentions**: comments, tests, migrations, and model declarations do not count.
- **Indirect reads** via `settings.EXPORT_FIELDS` count; field lists from the environment are `insufficient`.
- **External readers** are registered in YAML, not code.

## Build and verify

```bash
docker build -t lh10_column_drop_s3 longhorizon/tasks/lh10_column_drop_s3/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
