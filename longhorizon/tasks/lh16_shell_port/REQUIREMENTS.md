# lh16_shell_port: what completing it requires

Seed 1. Probes: faithful translation: reproducing a tool's exact observable behaviour.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `py/<name>.py` for each of 40 scripts.
- Grading: Per script: the fraction of five hidden input sets (including empty and one-line inputs) on which the port's stdout equals the pipeline's byte for byte. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 40 independent scripts. For each one the agent must work out exactly what each tool in the pipeline does to edge cases (ties, padding, number formatting, missing fields, empty input), port it, and diff against the script on samples. That is about 8 turns and 1,800 tokens of reasoning and output per script.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **55.4 min** |
| single agent, ideal (batches every read; floor) | **21.6 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.6 min** (peak 5,293 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 40 scripts (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **`uniq -c` padding** and **`sort -rn` ties** (the last-resort comparison reverses too).
- **awk number formatting**: large or fractional sums print as `%.6g`.
- **`cut`** prints lines without the delimiter unchanged; **`join`** drops unpaired lines and multiplies duplicates; **`paste`** pads the shorter file.
- **Empty input** must print exactly what the pipeline prints (often nothing, `grep -c` prints 0).

## Build and verify

```bash
docker build -t lh16_shell_port longhorizon/tasks/lh16_shell_port/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
