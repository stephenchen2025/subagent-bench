# lh7_cve_impact_s1: what completing it requires

Family `lh7_cve_impact`, seed 1. Probes: reachability and indirection (F4); `insufficient` (F3).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/impact/impact.json`.
- Grading: Per service, the verdict. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 52 independent services. For each one the agent must read the lockfile and manifest, find every yamlish call however it is spelled, check the loader and the input's origin, follow vendored wrappers, and check routes.py. That is about 6 turns and 1,500 tokens of reasoning and output per service.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **57.9 min** |
| single agent, ideal (batches every read; floor) | **23.9 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.7 min** (peak 8,669 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 52 services (78,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **The lock pins the version**, not the manifest; either can look safer than the other.
- **Spelling varies**: aliases, helpers, `stream=`, SafeLoader via a variable.
- **Indirection**: `configkit.parse_payload` does the unsafe load; the service never imports yamlish.
- **Trusted inputs** (files in the image) and **unrouted handlers** are not reachable.
- **No lockfile** with a range spanning the fix: `insufficient`.

## Build and verify

```bash
docker build -t lh7_cve_impact_s1 longhorizon/tasks/lh7_cve_impact_s1/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
