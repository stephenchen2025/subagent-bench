# lh15_perf_fixes: what completing it requires

Seed 1. Probes: optimisation under an exact-equivalence contract.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: rewritten modules under `perf/`.
- Grading: Per function: identical results to the original on small hidden inputs and to a reference on a large one, within the time limit. All or nothing per function; reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 40 independent functions. For each one the agent must find the complexity bottleneck, pick a faster algorithm, and make sure it preserves every observable detail: order, tie-breaking, duplicate pairing, case handling, edge sizes. That is about 7 turns and 1,800 tokens of reasoning and output per function.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **50.1 min** |
| single agent, ideal (batches every read; floor) | **21.3 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.1 min** (peak 4,008 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 40 functions (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Tie-breaking.** `max(words, key=words.count)` returns the first of several tied words; `Counter.most_common` must be used carefully to match.
- **Duplicate semantics.** Pair counting over repeated values, and joins that must keep right-row order.
- **Variants.** Case-insensitive, absolute-value, minimum-instead-of-maximum and sum-instead-of-list versions sit next to their plain siblings.
- **Edge sizes.** Empty inputs, windows as large as the input, limits below 3.

## Build and verify

```bash
docker build -t lh15_perf_fixes longhorizon/tasks/lh15_perf_fixes/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
