# lh11_test_authoring: what completing it requires

Seed 1. Probes: writing tests from a spec (graded by mutation, not by coverage).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less` and `pytest`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `tests/test_<module>.py` for each of the 40 modules.
- Grading: Per module: the fraction of planted mutants (one-line changes that each break one sentence of the docstring) that the agent's tests kill; 0 if the tests fail on the real code or read the source. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 40 independent modules. For each one the agent must read the function and its docstring, enumerate every edge and error case the docstring states, and write a test that pins each. That is about 7 turns and 2,000 tokens of reasoning and output per module.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **52.9 min** |
| single agent, ideal (batches every read; floor) | **23.7 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **8.4 min** (peak 5,031 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 40 modules (80,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Smoke tests score near zero.** Mutants break boundaries (`<` vs `<=`), rounding modes, error paths and ordering rules, which only edge-case tests catch.
- **Variants differ subtly** (lowercase vs uppercase numerals, `-` vs `_` separators, 2 vs 3 decimal places), so tests copied from one module fail on its sibling.
- **Reading the source is refused**, so fingerprinting cannot stand in for testing.

## Build and verify

```bash
docker build -t lh11_test_authoring longhorizon/tasks/lh11_test_authoring/environment
harbor run -p longhorizon/tasks -a oracle          # the oracle must score 1.0
```
