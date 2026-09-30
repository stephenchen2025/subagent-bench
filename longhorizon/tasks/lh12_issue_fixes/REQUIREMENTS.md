# lh12_issue_fixes: what completing it requires

Seed 1. Probes: triage judgement over a mixed backlog: bug, duplicate, misreading, stale report.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less` and `pytest`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: code fixes under `shop/` and `/workspace/triage.json`.
- Grading: Per issue: the resolution is right (duplicates must name the original), AND the module meets a hidden spec test afterwards. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 40 independent issues. For each one the agent must reproduce the reported call, compare with the spec, decide which of four outcomes applies, and fix the code only if it is really broken. That is about 7 turns and 1,800 tokens of reasoning and output per issue.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **50.9 min** |
| single agent, ideal (batches every read; floor) | **21.6 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.3 min** (peak 5,863 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 40 issues (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Not every report is a bug.** A fifth of reporters misread the spec (half-up vs banker's rounding, a grace period, a cap). Changing the code to match them fails the spec test.
- **Stale reports.** Some issues were filed against an old version; the current code already gives the expected value.
- **Duplicates** report the same defect with a different input; they must be linked to the earlier issue, which requires comparing root causes, not symptoms.

## Build and verify

```bash
docker build -t lh12_issue_fixes longhorizon/tasks/lh12_issue_fixes/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
