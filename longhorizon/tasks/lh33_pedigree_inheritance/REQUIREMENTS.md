# lh33_pedigree_inheritance: what completing it requires

Seed 1. Probes: a proof per unit: which transmissions each mode forbids, through unexamined carriers.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/modes.json`.
- Grading: Per family, all or nothing: exactly the set of modes the pedigree allows. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 50 independent familys. For each one the agent must for each of five modes, try to assign genotypes that fit every phenotype: follow sons' X from their mothers, carriers through unexamined members, and the non-carrier spouses. That is about 6 turns and 1,600 tokens of reasoning and output per family.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **56.0 min** |
| single agent, ideal (batches every read; floor) | **24.1 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.7 min** (peak 7,173 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 50 familys (80,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Married-in spouses** who are unaffected carry nothing, which rules out AR in many families.
- **Adoptees** are listed with parents who are not biological.
- **Not examined** members can be carriers or affected.
- **X-linked**: a son's X comes from his mother; an affected father passes XLD to every daughter.
- **Textbook heuristics** ("skips a generation, so recessive") pick one mode; the answer is the full set.

## Build and verify

```bash
docker build -t lh33_pedigree_inheritance longhorizon/tasks/lh33_pedigree_inheritance/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
