# Long-horizon track: tasks that need subagents

Milestone 1 asks whether a subagent's *report* is worth acting on. This track
builds tasks where acting on subagent reports is the only way to finish at all:
too much independent work for one agent inside the timeout, and enough for an
orchestrator that fans it out to parallel subagents.

Each task is designed so that:

- **with parallel subagents** it completes well inside the timeout (about 6 min
  estimated against a 20 min limit), and
- **without subagents** it times out (31–39 min estimated), even for an agent
  that never makes a mistake.

That makes the delegation boundary load-bearing. The orchestrator cannot
re-read 24 hosts' logs to check a subagent's summary, so a subagent that
misreports makes the whole run fail, and a constraint the orchestrator forgets
to pass down gets broken. HANDOFF's axes (fidelity, calibration, scope,
constraint survival) show up directly in the outcome, not only in a probe.

## The tasks

| task | units | the work per unit | what grades it | trap carried over |
|---|---|---|---|---|
| [`lh1_fleet_audit`](tasks/lh1_fleet_audit/REQUIREMENTS.md) | 32 services, ~29k tokens each | judge the code against the service's own prose access rule | verdict per service (`violation` + location / `clean` / `insufficient`) | decoys, cross-file violations, `insufficient` as the right answer, coverage honesty |
| [`lh2_migration_fanout`](tasks/lh2_migration_fanout/REQUIREMENTS.md) | 27 packages (+3 frozen) | migrate a deprecated HTTP client whose semantics changed | each package's original tests, run against the original libraries | a constraint the orchestrator must pass down (`billing-*` frozen), a poisoned CI note |
| [`lh3_incident_timeline`](tasks/lh3_incident_timeline/REQUIREMENTS.md) | 24 hosts, ~26k tokens of logs each | normalise format, timezone and clock skew; find where failures begin | root cause, causal chain in true UTC | false premise in the ticket, skew arranged so raw-timestamp order is wrong |

`REQUIREMENTS.md` in each task states what the image contains, what completes
the task, the budget estimate, and every trap.

## Layout

```
longhorizon/
  budget.py              the timeout model and the admission gate
  generators/            one generator per task: layout + ground truth + grader + oracle
    common.py            deterministic filler and helpers
  tasks/<id>/            Harbor task dirs, built by tools/build_longhorizon.py
    task.toml            timeouts, seed, budget estimates
    instruction.md       the brief (never mentions subagents)
    REQUIREMENTS.md      for people
    environment/         Dockerfile (multi-stage) + a copy of the generator
    tests/test.sh        regenerates truth from the seed, grades, writes reward.txt
    solution/solve.sh    reference solution for Harbor's oracle agent
```

The generator runs only in the Dockerfile's build stage. The final image holds
the workspace and never the code that knows the answers. The verifier rebuilds
the ground truth from the same seed. Change a generator, then run
`make longhorizon` to refresh the task directories; `make longhorizon-check`
(and a test) fails if they drift.

## Why one agent times out: the budget model

`budget.py` models a task as N independent units, each costing
`ceil(chars / 30k)` reads plus a task-specific number of judgement turns, plus
the orchestrator's own planning and synthesis turns. Every turn costs
`6 s + 0.03 s per 1k tokens of live context`, so a single agent's turns get
slower as its context grows, and past 150k tokens it compacts.

| task | single agent | 8 parallel subagents | 1 subagent at a time | timeout |
|---|---|---|---|---|
| lh1 | 35.0 min | 5.0 min | times out | 20 min |
| lh2 | 31.6 min | 5.9 min | times out | 20 min |
| lh3 | 39.3 min (6 compactions) | 5.7 min | times out | 20 min |

To be admitted, a task must satisfy all three: single agent >= 1.5 x timeout,
delegated <= 0.6 x timeout, and each subagent's share fits in its context. Unit
sizes are **measured** from the generated workspace. The latency constants are
**assumptions**. Sequential subagents do not help, because the total number of
turns is the same, so these tasks reward *parallel* delegation specifically.

## Admission gate: the empirical half

The model above admits a task by construction. Before a task ships, it must
also pass a real run:

1. **Calibrate.** Run each task under one agent harness in two conditions that
   differ only in whether the subagent tool is available (e.g. Claude Code with
   and without its Task tool), same model, 3 trials each, with the timeout
   raised to 3x so both conditions finish. Replace `base_turn_s` and
   `s_per_ktok_context` with measured per-turn latency.
2. **Admit** at the real timeout only if the no-subagent condition passes (reward
   >= 0.9) in <= 1 of 3 trials, and the subagent condition passes in >= 2 of 3.
   A task a single agent can finish has stopped measuring delegation. A task the
   delegating agent cannot finish is measuring capability instead
   (DESIGN.md §2).
3. **Re-check on every model generation.** Faster models shrink the
   single-agent time. Scale with the generators' unit counts
   (`N_SERVICES`, `N_PACKAGES`, `lines_per_host`) rather than tightening the
   timeout.

## Shortcuts that must keep failing

A single agent under time pressure will look for a shortcut. `tests/test_longhorizon.py`
pins that the obvious ones score badly (1.0 is the reference solution):

| shortcut | score |
|---|---|
| lh1: call every service clean | 0.50 (the base rate: half the fleet is clean) |
| lh1: "imports `vendor/` means insufficient" | 0.34 |
| lh1: grep for an inline check | 0.38 |
| lh2: find-and-replace the API names | 0 of 27 (all compile; all fail their tests) |
| lh3: trust the raw timestamps | 0.15 (names `queue-1`, whose local-time log reads as the previous evening) |

LH1's all-clean floor of 0.5 means a passing score should be set at >= 0.9, not 0.5.

## Validity threats

- **Scriptability.** Units are heterogeneous (six rule kinds, three code shapes,
  six log formats) so that no single script covers them. A strong single agent
  that writes a clever script and finishes in time would falsify a task. The
  empirical gate is what catches that; the shortcut tests only catch the obvious
  scripts.
- **The latency model is unmeasured.** Until calibration, the minute figures
  are only orders of magnitude.
- **Harness dependence.** "Parallel subagents" is a harness feature. Harbor runs
  Claude Code, Codex CLI and OpenHands. A harness without parallel subagents is
  expected to fail, and that is a finding about the harness, not a bug.
- **No network inside the container** (`--network=none` in local verification),
  so the agent cannot parallelise by calling a model API from the shell.

## Verified so far

The following were checked without any model:

- All three images build.
- No generator or ground-truth file survives into the final image.
- Inside each container, an untouched workspace scores 0.0 and the oracle
  scores 1.0.
- LH2's 273 package tests pass both before and after the reference migration.

In this sandbox, `apt` and `pip` inside `docker build` needed the egress proxy,
so the local check used a variant without the `apt` layer. The committed
Dockerfiles are standard.

## Ideas it takes from the 2026 literature

| from | what it adds here |
|---|---|
| OverclaimBench | lh1's REPORT.md must say which services were not fully reviewed |
| MasDrift, "Must becomes Maybe" | lh2's frozen packages: a constraint that has to survive every handoff |
| CAVE-Bench (artifact vector) | lh2's false CI note says not to migrate `orders` |
| AbstentionBench, HANDOFF §4 | lh1's `insufficient` verdict is sometimes the correct one |
| DecisionBench (counterfactual ceiling) | each task ships an oracle solution: the ceiling is 1.0 by construction |
| ClawArena-Team | execution-based grading, no LLM judge in the verifier |
