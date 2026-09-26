# lh6_flake_triage_s3: what completing it requires

Family `lh6_flake_triage`, seed 3. Probes: evidence split across source and runs; `insufficient` as a verdict (F3).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/triage/triage.json`.
- Grading: Per test, the cause category. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent flaky tests. For each one the agent must read the module under test (which touches two flaky mechanisms), read six CI runs, and find which run attribute tracks the failures. That is about 6 turns and 1,500 tokens of reasoning and output per flaky test.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **60.3 min** |
| single agent, ideal (batches every read; floor) | **25.6 min** (1 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.8 min** (peak 26,149 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 flaky tests (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Ambiguous source.** Every function touches its real mechanism and a decoy one.
- **Generic failures.** Every failure is the same `assert {...} == {...}`; the cause is the attribute that correlates with failing runs. Every other attribute varies at random and never matches exactly.
- **No correlation** plus an unseeded RNG means `unseeded_random`.
- **Truncated logs** mean `insufficient`.

## Build and verify

```bash
docker build -t lh6_flake_triage_s3 longhorizon/tasks/lh6_flake_triage_s3/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
