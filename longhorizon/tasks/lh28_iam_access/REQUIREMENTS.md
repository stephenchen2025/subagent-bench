# lh28_iam_access: what completing it requires

Seed 1. Probes: exact policy evaluation over each principal's own set of documents.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/access.json`.
- Grading: Per principal, all or nothing: all five answers right. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent principals. For each one the agent must collect the principal's direct and group policies and boundary, then evaluate five requests through wildcards, conditions, explicit denies and the boundary. That is about 6 turns and 1,500 tokens of reasoning and output per principal.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.4 min** |
| single agent, ideal (batches every read; floor) | **22.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.4 min** (peak 8,766 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 principals (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Explicit deny wins**, often from a group policy.
- **Permission boundaries** cut allows the policies grant.
- **Case**: actions match case-insensitively, resources case-sensitively (`Q3.CSV`).
- **Conditions**: IP ranges, team tags, and dates that expired before the request.

## Build and verify

```bash
docker build -t lh28_iam_access longhorizon/tasks/lh28_iam_access/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
