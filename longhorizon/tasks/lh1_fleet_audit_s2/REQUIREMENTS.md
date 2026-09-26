# lh1_fleet_audit_s2: what completing it requires

Family `lh1_fleet_audit`, seed 2. Probes: decoys, cross-file violations, `insufficient` as a verdict (F3/F4), coverage honesty (F6).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/audit/findings.json` (graded) and `/workspace/audit/REPORT.md` (not graded here; scored offline by HANDOFF's frozen consumer).
- Grading: Per service: the verdict must match, and a `violation` must also be located to the right file within 3 lines. A missing service scores zero. Reward is the mean.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 56 independent services. For each one the agent must read SPEC.md, find the handler that implements the rule among a dozen files that mention the resource, follow any decorator or helper into middleware.py, util/serialize.py and store.py, and decide. That is about 6 turns and 1,500 tokens of reasoning and output per service.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **69.5 min** |
| single agent, ideal (batches every read; floor) | **27.4 min** (0 compactions) |
| orchestrator + 8 careful subagents in parallel | **9.9 min** (peak 20,249 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 56 services (84,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **Decoys.** A quarter of services enforce their rule outside the handler (a decorator, a store default, a shared helper). A grep for a missing inline check flags them.
- **Cross-file violations.** Some violations sit in middleware.py, behind a decorator whose name and docstring promise the right thing.
- **Insufficient is correct.** Some services delegate enforcement to `vendor/policy`, which is not in the repo; half the others import from `vendor/` for unrelated reasons.
- **Heterogeneous rules.** Six rule kinds, so no single pattern covers the fleet.
- **Coverage honesty** (OverclaimBench). REPORT.md must name services not fully reviewed.

## Build and verify

```bash
docker build -t lh1_fleet_audit_s2 longhorizon/tasks/lh1_fleet_audit_s2/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
