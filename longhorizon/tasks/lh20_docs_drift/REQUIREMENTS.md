# lh20_docs_drift: what completing it requires

Seed 1. Probes: documentation made exactly true to code, including values the code computes.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: updated `docs/cli/<tool>.md` for 56 tools.
- Grading: Per tool: the longest in-order sequence of rows matching the table derived from the parser, over the larger of the expected and submitted row counts. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent tools. For each one the agent must read the parser, resolve every default (constants, expressions, environment fallbacks, inverted flags), drop hidden options, and rewrite the table in the house format. That is about 6 turns and 1,300 tokens of reasoning and output per tool.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **57.1 min** |
| single agent, ideal (batches every read; floor) | **22.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.2 min** (peak 5,015 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 tools (72,800 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Computed defaults**: `default=2 * DEFAULT_RETRIES` must be documented as the number.
- **Environment defaults** use the `$NAME` or `fallback` form.
- **`--no-color` defaults to `true`**; `store_true` flags to `false`.
- **Hidden options** have leaked into some pages and must be removed; so must the long-gone `--legacy-output`.
- **Stale choices and defaults** look plausible; only the code says which are wrong.

## Build and verify

```bash
docker build -t lh20_docs_drift longhorizon/tasks/lh20_docs_drift/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
