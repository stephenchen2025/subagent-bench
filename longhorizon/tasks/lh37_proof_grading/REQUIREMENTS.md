# lh37_proof_grading: what completing it requires

Seed 1. Probes: step-by-step verification where the same sentence is valid or invalid depending on its numbers.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/marks.json`.
- Grading: Per proof: the first invalid step (0 if valid), exactly. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 48 independent proofs. For each one the agent must check every step against the claim, the earlier steps and the numbers in it: recompute each algebraic line, and ask whether each standard move (divide, take a root, use divisibility) is allowed here. That is about 5 turns and 1,500 tokens of reasoning and output per proof.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **46.3 min** |
| single agent, ideal (batches every read; floor) | **21.6 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **7.8 min** (peak 4,704 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 48 proofs (72,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **A true claim, an invalid proof**: sqrt(12) is irrational, but "12 divides p^2, so 12 divides p" is false.
- **Domains**: dividing by 1 - r for every real r; square roots for every nonzero x.
- **Degenerate numbers**: the bracket is "a nonzero constant" unless b + c = 0.
- **Slips** in one line (a wrong next term, a dropped factor) that later lines repeat: the FIRST is the answer.
- **Base cases** that are false for the given modulus.

## Build and verify

```bash
docker build -t lh37_proof_grading longhorizon/tasks/lh37_proof_grading/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
