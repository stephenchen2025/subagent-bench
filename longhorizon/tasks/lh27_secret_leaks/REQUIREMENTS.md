# lh27_secret_leaks: what completing it requires

Seed 1. Probes: separating real findings from scanner noise with several independent checks per hit.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/leaks.json`.
- Grading: Per repository, all or nothing: the exact set of leaks. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 60 independent repositorys. For each one the agent must scan the repo, and for every hit check format, tracking, revocation (by hashing) and placeholder status. That is about 6 turns and 1,200 tokens of reasoning and output per repository.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **61.3 min** |
| single agent, ideal (batches every read; floor) | **22.3 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **10.1 min** (peak 8,181 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 60 repositorys (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Untracked files** (.env, local/) hold real-looking keys that were never committed.
- **Revoked keys** can only be ruled out by hashing them.
- **Documented placeholders** and **test-mode keys** match scanner patterns.
- **Secret-sounding names** with harmless values.
- **Assembled and encoded tokens** (two concatenated literals, base64 in config) that pattern scanners miss.

## Build and verify

```bash
docker build -t lh27_secret_leaks longhorizon/tasks/lh27_secret_leaks/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
