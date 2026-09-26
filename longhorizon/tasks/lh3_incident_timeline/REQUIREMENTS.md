# lh3_incident_timeline: what completing it requires

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (seed 1, committed as a git baseline). There is no network access and no model access from inside the container, so the agent cannot parallelise by starting a second copy of itself. Only its harness's own subagents can do that.

The generator runs in a throwaway build stage. The ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/timeline.json`.
- Grading: 0.1 for rejecting the ticket's premise, 0.3 for the root cause (host and kind), 0.4 for recall of the 10 causal events (host and kind match, time within 6 s of true UTC), 0.1 for their pairwise order, 0.1 for precision.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 24 independent hosts. Each one requires the agent to work out the host's log format and timezone, read its clock offset, scan ~26k tokens of log for incident events among routine errors, find where each sustained failure begins, and convert those times to true UTC: about 9 turns per host, so roughly 216 turns in sequence for a single agent, at an ever-longer context.

| | single agent | orchestrator + subagents |
|---|---|---|
| estimated wall clock | **39.3 min** | **5.7 min** (8 in parallel) |
| timeout | 20 min | 20 min |
| peak context | grows to all 24 hosts (~727,428 tokens; 6 compactions) | 105,796 tokens per subagent |

Gate (longhorizon/budget.py): single agent >= 1.5 x timeout, delegated <= 0.6 x timeout, subagent fits in context. Result: **admitted** (single_agent_times_out, delegated_fits_timeout, subagent_fits_context).

These are estimates. The unit sizes are measured from the generated workspace, but turn latency is an assumption until the calibration run in `longhorizon/README.md` replaces it. Subagents run one after another do not help: the work is the same total number of turns. The task rewards **parallel** delegation.

## Traps

- **False premise** (F2). The ticket says db-primary failed first. It failed last.
- **Clock skew by design.** Ordered by raw timestamps, api-6's retry storm looks like the first event and looks earlier than the real root cause. Only per-host correction (chrony.log) gets the order right.
- **Local time.** The queue hosts log in America/Chicago without a year, so their 02:10 UTC events read `Sep 13 21:10`.
- **Decoys.** A healthy certificate reload on another load balancer 15 minutes earlier, an autovacuum warning on db-primary, a failed cron job, and a signing-key rotation, all inside the window.
- **Onset, not presence.** Handshake errors occur at a low rate on every edge host all night. The event is where the rate on one host jumps.
- **Every host must be read.** The first occurrence of a kind that fires on several hosts can only be found after all of them are corrected.

## Build and verify

```bash
docker build -t lh3_incident_timeline longhorizon/tasks/lh3_incident_timeline/environment
harbor run -d longhorizon/tasks -a oracle          # oracle must score 1.0
```
