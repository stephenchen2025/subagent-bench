# lh3_incident_timeline_s3: what completing it requires

Family `lh3_incident_timeline`, seed 3. Probes: a false premise in the brief (F2); decoys (F4).

## What the agent gets

A `python:3.12-slim` container with `git`, `ripgrep`, `jq` and `less`, and a generated workspace at `/workspace` (committed as a git baseline). There is no network access and no model access inside the container, so the agent cannot parallelise by starting a second copy of itself: only its harness's own subagents can do that. The generator runs in a throwaway build stage; the ground truth is never in the final image, and the verifier regenerates it from the seed.

## What completes the task

- Deliverable: `/workspace/answer/timeline.json`.
- Grading: 0.1 for rejecting the ticket's premise, 0.3 for the root cause (host and kind), 0.4 for recall of the 10 causal events (host and kind, time within 6 s of true UTC), 0.1 for their pairwise order, 0.1 for precision.
- Agent timeout: 20 minutes of wall clock (`task.toml`).

## Why one agent times out and a delegating one does not

There are 24 independent hosts. For each one the agent must work out the host's log format and timezone, read its clock offset, scan ~26k tokens of log for where each sustained failure begins, and convert to true UTC. That is about 8 turns and 1,500 tokens of reasoning and output per host.

| | estimate |
|---|---|
| single agent, careful (unit by unit) | **45.5 min** |
| single agent, ideal (batches every read; floor) | **29.5 min** (5 compactions) |
| orchestrator + 8 careful subagents in parallel | **6.9 min** (peak 103,874 tokens per subagent) |
| timeout | 20 min |

What even the ideal single agent cannot batch away is the reasoning and output for 24 hosts (36,000 tokens, decoded one after another). Parallel subagents decode theirs at the same time. Subagents run one after another do not help; the task rewards **parallel** delegation.

Gate: **admitted** (ideal_single_agent_times_out: True, careful_single_agent_times_out: True, delegated_fits_timeout: True, subagent_fits_context: True). Unit sizes are measured from the generated workspace; latency, decode speed and output tokens per unit are assumptions until the calibration run in `longhorizon/README.md`.

## Traps

- **False premise.** The ticket says db-primary failed first. It failed last.
- **Clock skew, solved per seed.** Ordered by raw timestamps, a decoy api host's retry storm reads as earlier than the real root cause, even with timezones corrected.
- **Local time.** The queue hosts log in America/Chicago without a year.
- **Decoys.** A healthy certificate reload on another load balancer, an autovacuum warning, a failed cron job and a key rotation, all inside the window.
- **Onset, not presence.** Handshake errors occur all night on every edge host; the event is where one host's rate jumps.

## Build and verify

```bash
docker build -t lh3_incident_timeline_s3 longhorizon/tasks/lh3_incident_timeline_s3/environment
harbor run -d longhorizon/tasks -a oracle          # the oracle must score 1.0
```
