# lh36_reaction_yields: what completing it requires

Seed 1. Probes: chemical arithmetic where each report measures its reagents differently.

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/yields.json`.
- Grading: Per report, all or nothing: moles of each reagent within 0.5 %; limiting reagent; theoretical yield within 0.5 %; percent yield within 0.5 points. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent lab reports. For each one the agent must balance the equation, convert each reagent to moles (purity, hydrate water, density, molarity), compare moles per coefficient, and compute the theoretical and percent yield. That is about 5 turns and 1,400 tokens of reasoning and output per lab report.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **53.1 min** |
| single agent, ideal (batches every read; floor) | **23.8 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.7 min** (peak 6,188 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 lab reports (78,400 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Coefficients**: 2 Al + 3 CuCl2 -> 2 AlCl3 + 3 Cu; 4 Fe + 3 O2 -> 2 Fe2O3.
- **Hydrates**: the mass includes the water of crystallisation.
- **Purity, density, molarity**: every reagent is measured differently.
- **"Used in excess"** notes that are wrong.
- **The product's coefficient** (3 Cu per 2 Al) scales the theoretical yield.

## Build and verify

```bash
docker build -t lh36_reaction_yields longhorizon/tasks/lh36_reaction_yields/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
