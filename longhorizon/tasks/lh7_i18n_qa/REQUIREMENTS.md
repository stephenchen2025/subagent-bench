# lh7_i18n_qa: what completing it requires

Seed 1. Probes: per-language rules applied across a whole catalogue.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/l10n_errors.json`.
- Grading: Per locale, all or nothing: the exact set of errors. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent locales. For each one the agent must diff the catalogue against the source key by key: placeholders (including plural branches), the language's plural categories, character-counted limits, untranslated strings, missing and extra keys. That is about 6 turns and 1,400 tokens of reasoning and output per locale.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **59.1 min** |
| single agent, ideal (batches every read; floor) | **24.0 min** (1 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.4 min** (peak 26,481 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 locales (67,200 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Plural categories differ by language** (Polish four, Japanese one, Arabic six).
- **Placeholders inside plural branches.**
- **Characters, not bytes**: a string exactly at its limit in accented letters is fine.
- **Brand names** are legitimately identical to English.
- **A missing key** is only E5, not also E1-E4.

## Build and verify

```bash
docker build -t lh7_i18n_qa longhorizon/tasks/lh7_i18n_qa/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
