# lh18_docker_hardening: what completing it requires

Seed 1. Probes: applying a policy precisely, per unit, with facts drawn from each unit's own docs.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: edited `services/<svc>/Dockerfile` for 48 services.
- Grading: Per service, all or nothing: the grader's policy checker finds no broken rule, and every COPY/CMD/ENTRYPOINT/EXPOSE/WORKDIR line and the harmless ENV survive. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent Dockerfiles. For each one the agent must check all six rules against this Dockerfile, look up digests and successors, read the service README for its health endpoint, and edit without dropping behaviour. That is about 6 turns and 1,500 tokens of reasoning and output per Dockerfile.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **52.1 min** |
| single agent, ideal (batches every read; floor) | **21.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.4 min** (peak 6,076 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 Dockerfiles (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Secrets by value, not name.** `ENV SECRET_ROTATION_DAYS=30` must stay; `ARG GITHUB_TOKEN=ghp_...` must go.
- **Deprecated tags** must move to their successor, and build stages need pinning too.
- **Health endpoints differ per service**; a generic `/health` check fails half of them.
- **`USER root` at the end** still breaks R2.

## Build and verify

```bash
docker build -t lh18_docker_hardening longhorizon/tasks/lh18_docker_hardening/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
