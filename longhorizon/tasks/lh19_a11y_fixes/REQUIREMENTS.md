# lh19_a11y_fixes: what completing it requires

Seed 1. Probes: precise markup fixes whose values come from per-element data, with no collateral change.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: fixed `site/pages/*.html`.
- Grading: Per page, all or nothing: an HTML checker finds no rule broken, and every other element, attribute and text is unchanged. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent pages. For each one the agent must find every failing element on the page, take each fix's value from the right place (pages.json, data-description, data-label, data-action, title), and fix heading levels in order. That is about 6 turns and 1,500 tokens of reasoning and output per page.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **51.1 min** |
| single agent, ideal (batches every read; floor) | **21.5 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.4 min** (peak 4,704 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 pages (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Locales are per page**, only in pages.json.
- **Decorative images need `alt=""`**, not a description.
- **Labels need matching ids**, and a field without an id gets its name.
- **Heading fixes cascade**: lowering one heading can change what the next may be.
- **Collateral edits** (reformatted text, dropped attributes) fail the page.

## Build and verify

```bash
docker build -t lh19_a11y_fixes longhorizon/tasks/lh19_a11y_fixes/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
