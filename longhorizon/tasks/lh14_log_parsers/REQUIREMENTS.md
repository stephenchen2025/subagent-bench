# lh14_log_parsers: what completing it requires

Seed 1. Probes: inferring a format from samples and normalising it exactly; graded on held-out logs.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `parsers/<format>.py` with `parse(text) -> list[dict]` for each of 32 formats.
- Grading: Per format: the fraction of held-out records returned exactly (UTC timestamp to the millisecond, canonical level, unescaped message with continuation lines, request id or null). Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 32 independent log formats. For each one the agent must work out the timestamp style and offset, the level encoding, the layout and its escaping, and any continuation lines -- from a note if there is one, from the sample if not -- then write and check a parser. That is about 7 turns and 2,200 tokens of reasoning and output per log format.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **51.2 min** |
| single agent, ideal (batches every read; floor) | **24.3 min** (1 compactions) |
| orchestrator + 8 careful subagents in parallel | **7.3 min** (peak 20,893 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 32 log formats (70,400 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Offsets.** ISO-with-offset and CLF timestamps are local; the schema wants UTC.
- **Level synonyms.** `warning`/`fatal`, single letters, and Python's numeric levels.
- **Escaping.** key=value messages escape quotes and newlines; CSV doubles quotes.
- **Continuation lines** belong to the previous record's message.
- **Held-out grading.** A parser tuned to quirks of the sample, or one that hardcodes it, fails.
- **Half the formats are undocumented.**

## Build and verify

```bash
docker build -t lh14_log_parsers longhorizon/tasks/lh14_log_parsers/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
