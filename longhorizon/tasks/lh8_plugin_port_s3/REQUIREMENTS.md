# lh8_plugin_port_s3: what completing it requires

Family `lh8_plugin_port`, seed 3. Probes: parallel siblings over shared state (F7).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less` and `pytest`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: ported plugins, the registry, and CHANGELOG.md under `/workspace`.
- Grading: Per plugin: its original tests pass against the agent's port and registry, and its CHANGELOG line exists (0.9). The registry itself sorted, complete and duplicate-free (0.1).
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 36 independent plugins. For each one the agent must read the v1 plugin (whose dry-run key differs per plugin), write the v2 class, register it, and log it. That is about 8 turns and 2,500 tokens of reasoning and output per plugin.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **57.5 min** |
| single agent, ideal (batches every read; floor) | **26.6 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.9 min** (peak 7,482 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 36 plugins (90,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Shared files.** Every port edits `pluginapi/registry.py` and `CHANGELOG.md`. Subagents that each rewrite them overwrite each other: the last of 8 writers leaves 4 of 36 plugins registered (reward 0.1). The orchestrator must own the shared edits.
- **Per-plugin dry-run keys** (`dry`, `dry_run`, `simulate`, `noop`), named only in each plugin's docstring.

## Build and verify

```bash
docker build -t lh8_plugin_port_s3 longhorizon/tasks/lh8_plugin_port_s3/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
