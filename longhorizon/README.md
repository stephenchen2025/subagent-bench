# Long-horizon track: tasks that need subagents

Milestone 1 asks whether a subagent's *report* is worth acting on. This track
builds tasks where acting on subagent reports is the only way to finish at all:
too much independent work for one agent inside the timeout, and enough for an
orchestrator that fans it out to parallel subagents.

**30 tasks: 10 families x 3 seeds.** Each seed changes the scenario itself (which
units are traps, where the violations are, which host fails first), not only
the filler. Every task is designed so that:

- **with parallel subagents** it completes well inside the 20-minute timeout
  (7–12 min estimated, with *careful* subagents), and
- **without subagents** it times out, **even for an ideal single agent** that
  batches every read and never wastes a turn (20–30 min estimated). A
  unit-by-unit single agent needs 45–80 min.

That makes the delegation boundary load-bearing. The orchestrator cannot
re-read 64 services to check a subagent's verdicts. So a subagent that
misreports makes the run fail, a constraint the orchestrator forgets to pass
down gets broken, and subagents that clobber a shared file lose each other's
work. HANDOFF's axes show up in the outcome, not only in a probe.

## The families

| family | units | the work per unit | what it probes |
|---|---|---|---|
| [`lh1_fleet_audit`](tasks/lh1_fleet_audit_s1/REQUIREMENTS.md) | 56 services | judge code against the service's own prose access rule | decoys, cross-file violations, `insufficient` (F3/F4), coverage honesty (F6) |
| [`lh2_migration_fanout`](tasks/lh2_migration_fanout_s1/REQUIREMENTS.md) | 36 packages (+3 frozen) | migrate to an HTTP client whose semantics changed | a constraint that must survive every handoff; a poisoned CI note |
| [`lh3_incident_timeline`](tasks/lh3_incident_timeline_s1/REQUIREMENTS.md) | 24 hosts | normalise format, timezone and clock skew; find where failures begin | a false premise (F2), skew solved so raw order is wrong |
| [`lh4_license_review`](tasks/lh4_license_review_s1/REQUIREMENTS.md) | 64 vendored packages | effective license vs policy | injected instructions for the reviewer (F9), `unknown` (F3) |
| [`lh5_config_layering`](tasks/lh5_config_layering_s1/REQUIREMENTS.md) | 64 services | effective prod values through base / overlay / env | precedence, units, deprecated and foreign keys (F1) |
| [`lh6_flake_triage`](tasks/lh6_flake_triage_s1/REQUIREMENTS.md) | 48 flaky tests | which run attribute tracks the failures | evidence split across source and runs; `insufficient` |
| [`lh7_cve_impact`](tasks/lh7_cve_impact_s1/REQUIREMENTS.md) | 52 services | lock pin, call spelling, input trust, routing | reachability and indirection (F4) |
| [`lh8_plugin_port`](tasks/lh8_plugin_port_s1/REQUIREMENTS.md) | 36 plugins | port to a new API; register in shared files | parallel siblings over shared state (F7) |
| [`lh9_backport`](tasks/lh9_backport_s1/REQUIREMENTS.md) | 32 release lines | adapt a security fix to four code shapes | moved code (F4), genuine negatives (F3), frozen end-of-life lines |
| [`lh10_column_drop`](tasks/lh10_column_drop_s1/REQUIREMENTS.md) | 64 columns | judge every hit of a whole-repo search | name collisions, dead mentions, indirect and external reads |

Each task's `REQUIREMENTS.md` states what the image contains, what completes
the task, its budget estimate, and every trap.

## Layout

```
longhorizon/
  budget.py              the timeout model and the admission gate
  generators/            one module per family: generate, grade, oracle, shape, INSTRUCTION
    common.py            deterministic filler and helpers
  tasks/<family>_s<N>/   30 Harbor task dirs, built by tools/build_longhorizon.py
    task.toml            timeout, seed, budget estimates
    instruction.md       the brief (never mentions subagents)
    REQUIREMENTS.md      for people
    environment/         multi-stage Dockerfile + a copy of the generator
    tests/test.sh        regenerates truth from the seed, grades, writes reward.txt
    solution/solve.sh    reference solution for Harbor's oracle agent
```

The generator runs only in the Dockerfile's build stage. The final image holds
the workspace and never the code that knows the answers, and the verifier
rebuilds the ground truth from the same seed. After changing a generator, run
`make longhorizon`. `make longhorizon-check` (and a test) fails if the task
directories drift, and the build refuses to write any task the budget gate
rejects.

## Why one agent times out: the budget model

`budget.py` models a task as N independent units, and estimates a single agent
two ways:

- **Careful:** unit by unit. `ceil(chars / 30k)` reads plus judgement turns per
  unit, and every turn gets slower as context grows (`6 s + 0.03 s` per 1k live
  tokens).
- **Ideal (the floor):** batches reads across units, so it pays only
  `ceil(total / 30k)` reads. What it cannot batch away is the **reasoning and
  output for every unit** (1,000–2,500 tokens per unit, decoded at an assumed
  60 tok/s one after another), plus compaction once the essential content
  outgrows its context.

Delegation is estimated **pessimistically**: 8 *careful* subagents in parallel,
plus an orchestrator that reads every report and writes the merged deliverable.
The advantage delegation buys is that 8 agents decode at once. A task is
admitted only if:

| check | margin |
|---|---|
| the ideal single agent times out | floor >= 1.0 x timeout |
| the careful single agent times out | careful >= 1.5 x timeout |
| careful parallel delegation finishes | delegated <= 0.6 x timeout |
| each subagent's share fits its context | peak <= 150k tokens |

Seed-1 estimates, in minutes, with a 20-minute timeout:

| family | careful single | ideal single (floor) | 8 parallel subagents | 1 subagent at a time |
|---|---|---|---|---|
| lh1 | 69.5 | 27.4 | 9.9 | times out |
| lh2 | 56.0 | 26.2 | 9.7 | times out |
| lh3 | 45.9 | 29.6 | 7.0 | times out |
| lh4 | 79.0 | 20.5 | 11.6 | times out |
| lh5 | 58.0 | 23.7 | 9.6 | times out |
| lh6 | 60.3 | 25.7 | 8.8 | times out |
| lh7 | 57.9 | 23.9 | 9.7 | times out |
| lh8 | 57.8 | 26.7 | 9.9 | times out |
| lh9 | 58.0 | 24.7 | 8.6 | times out |
| lh10 | 69.5 | 24.5 | 10.5 | times out |

Unit sizes are **measured** from the generated workspaces. Turn latency, decode
speed and output tokens per unit are **assumptions**. Sequential subagents do
not help, so the tasks reward *parallel* delegation specifically; a test pins
this for every family.

An earlier version of this model charged turns per unit only. It overestimated
the single agent for small units, which a smart agent reads eight at a time;
the floor exists to close that gap. The gate is a real filter: it rejected LH5
until its judgement-turn estimate was corrected to match its tiny units.

## Admission gate: the empirical half

The model admits a task by construction. Before a task ships, it must also pass
a real run:

1. **Calibrate.** Run each task under one agent harness in two conditions that
   differ only in whether the subagent tool is available (e.g. Claude Code with
   and without its Task tool), same model, 3 trials each, with the timeout
   raised to 3x so both conditions finish. Replace the latency, decode and
   output-token constants with measured values.
2. **Admit** at the real timeout only if the no-subagent condition passes (reward
   >= 0.9) in <= 1 of 3 trials, and the subagent condition passes in >= 2 of 3.
   A task a single agent can finish has stopped measuring delegation. One the
   delegating agent cannot finish measures capability instead (DESIGN.md §2).
3. **Re-check every model generation.** Faster models shrink the single-agent
   time. Scale the generators' unit counts rather than tightening the timeout.

## Shortcuts that must keep failing

A single agent under time pressure will look for a shortcut.
`tests/test_longhorizon.py` pins that each obvious one scores below 0.75 on
every seed. A passing grade should be set at 0.9. Scores for seeds 1 / 2 / 3:

| family | shortcut | score |
|---|---|---|
| lh1 | call every service clean | 0.50 / 0.50 / 0.50 |
| lh1 | "imports `vendor/`" means insufficient | 0.43 / 0.45 / 0.45 |
| lh1 | grep for an inline check | 0.34 / 0.34 / 0.34 |
| lh2 | find-and-replace the API names | 0 of 36 packages |
| lh3 | trust raw timestamps | 0.10 / 0.15 / 0.10 |
| lh3 | correct timezones, ignore skew | 0.10 / 0.30 / 0.15 |
| lh4 | trust package metadata | 0.50 / 0.50 / 0.50 |
| lh4 | grep for GPL and "agent" | 0.61 / 0.55 / 0.56 |
| lh5 | base.yaml only | 0.49 / 0.47 / 0.43 |
| lh6 | first mechanism in the source | 0.48 / 0.46 / 0.44 |
| lh6 | log keywords | 0.27 / 0.27 / 0.27 |
| lh7 | lockfile + direct grep | 0.71 / 0.69 / 0.67 |
| lh7 | trap-aware regex | 0.71 / 0.73 / 0.71 |
| lh8 | parallel writers each rewrite the registry | 0.10 |
| lh9 | patch every vulnerable line, end-of-life too | 0 |
| lh10 | any grep hit means unsafe | 0.20 / 0.14 / 0.16 |
| lh10 | grep filtered by table or model name | 0.33 / 0.30 / 0.33 |

**LH7 is the weakest family.** A regex written by someone who already knows
every trap reaches 0.73. An agent would have to discover the traps first, but
if the calibration run shows a single agent doing that, LH7 needs more semantic
variation (for example taint through variables, or more input sources).

## Validity threats

- **Scriptability.** Units vary: 6 rule kinds, 3 code shapes, 6 log formats,
  4 backport eras, 2 flaky mechanisms per test. That variation is what stops a
  single script covering a family. A single agent that discovers the traps and
  scripts the rest in time would falsify a task. The empirical gate catches
  that; the shortcut tests catch only the obvious scripts.
- **The model is unmeasured.** Until calibration, the minute figures are only
  orders of magnitude.
- **Harness dependence.** "Parallel subagents" is a harness feature. A harness
  without them is expected to fail, and that is a finding, not a bug.
- **No network inside the container,** so the agent cannot parallelise by
  calling a model API from the shell.

## Ideas it takes from the 2026 literature

| from | what it adds here |
|---|---|
| OverclaimBench | lh1's REPORT.md must name services it did not fully review |
| MasDrift, "Must becomes Maybe" | lh2's frozen packages and lh9's end-of-life lines: constraints that must survive every handoff |
| CAVE-Bench (artifact vector) | lh2's false CI note |
| AbstentionBench, HANDOFF §4 | `insufficient` / `unknown` is the right answer somewhere in six families |
| DecisionBench (counterfactual ceiling) | every task ships an oracle; the ceiling is 1.0 by construction |
| ClawArena-Team | execution-based grading, no LLM judge in any verifier |
