# Long-horizon track: tasks that need subagents

Milestone 1 asks whether a subagent's *report* is worth acting on. This track
builds tasks where acting on subagent reports is the only way to finish at all:
too much independent work for one agent inside the timeout, and enough for an
orchestrator that fans it out to parallel subagents.

**30 tasks, one per family, and no two alike.** Each family is a different
kind of work in a different domain: code review, migrations, tests, SQL,
parsers, performance, ports, refactors, config, markup, docs, data cleaning,
finance, statistics, contracts, support, security, IAM, calendars, validators,
localisation. A test pins that no two families share a kind or a domain and
that no two briefs overlap by more than 15% of their word trigrams (the
largest overlap today is 5%). Every task is designed so that:

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

Each task's `REQUIREMENTS.md` states what the image contains, what completes
the task, its budget estimate, and every trap.

| task | kind of work | domain | units | what makes each unit its own work |
|---|---|---|---|---|
| [`lh1_fleet_audit`](tasks/lh1_fleet_audit/REQUIREMENTS.md) | compliance verdicts | service handler code | 56 services | each service's own prose access rule; decoys, vendored code, `insufficient` (F3/F4/F6) |
| [`lh2_migration_fanout`](tasks/lh2_migration_fanout/REQUIREMENTS.md) | API migration | internal Python library | 36 packages (+3 frozen) | changed client semantics; frozen packages and a poisoned CI note |
| [`lh3_incident_timeline`](tasks/lh3_incident_timeline/REQUIREMENTS.md) | root-cause timeline | incident response | 24 hosts | per-host format, timezone and clock skew; a false premise (F2) |
| [`lh4_license_review`](tasks/lh4_license_review/REQUIREMENTS.md) | licence verdicts | open-source licensing | 64 packages | effective licence vs metadata; instructions planted for the reviewer (F9) |
| [`lh5_config_layering`](tasks/lh5_config_layering/REQUIREMENTS.md) | resolved values | layered configuration | 64 services | base / overlay / env precedence, units, deprecated keys (F1) |
| [`lh6_flake_triage`](tasks/lh6_flake_triage/REQUIREMENTS.md) | cause classification | flaky tests | 48 tests | evidence split across source and six CI runs; `insufficient` |
| [`lh7_i18n_qa`](tasks/lh7_i18n_qa/REQUIREMENTS.md) | error list | localisation | 48 locales | the language's plural categories, character-counted limits, brand names |
| [`lh8_plugin_port`](tasks/lh8_plugin_port/REQUIREMENTS.md) | framework port | plugin system | 36 plugins | a new API, plus two shared files every port must touch (F7) |
| [`lh9_backport`](tasks/lh9_backport/REQUIREMENTS.md) | patch backport | release branches | 32 release lines | four code shapes; unaffected and end-of-life lines must stay untouched |
| [`lh10_column_drop`](tasks/lh10_column_drop/REQUIREMENTS.md) | impact analysis | database schema | 64 columns | name collisions, dead mentions, indirect and external reads |
| [`lh11_test_authoring`](tasks/lh11_test_authoring/REQUIREMENTS.md) | test writing | unit testing | 40 modules | each module's spec; graded by killing hidden mutants |
| [`lh12_issue_fixes`](tasks/lh12_issue_fixes/REQUIREMENTS.md) | bug fixes | issue tracker | 40 issues | fix, duplicate, not-a-bug or cannot-reproduce, judged against the spec |
| [`lh13_sql_reports`](tasks/lh13_sql_reports/REQUIREMENTS.md) | SQL queries | analytics database | 48 questions | business definitions (local days, FX, statuses); graded on a hidden database |
| [`lh14_log_parsers`](tasks/lh14_log_parsers/REQUIREMENTS.md) | parser writing | log formats | 32 formats | layout, timestamp and level conventions per format; graded on held-out logs |
| [`lh15_perf_fixes`](tasks/lh15_perf_fixes/REQUIREMENTS.md) | optimisation | algorithmic complexity | 40 functions | exact equivalence, including each copy's variant; a time budget |
| [`lh16_shell_port`](tasks/lh16_shell_port/REQUIREMENTS.md) | language port | shell scripts | 40 scripts | each tool's exact observable behaviour; no shelling out |
| [`lh17_flag_cleanup`](tasks/lh17_flag_cleanup/REQUIREMENTS.md) | dead-code removal | feature flags | 48 flags | the rollout history, not the label, decides; behaviour-preserving edits |
| [`lh18_docker_hardening`](tasks/lh18_docker_hardening/REQUIREMENTS.md) | file hardening | container images | 48 Dockerfiles | six policy rules; digests, successor tags and each service's own health endpoint |
| [`lh19_a11y_fixes`](tasks/lh19_a11y_fixes/REQUIREMENTS.md) | markup repair | web accessibility | 48 pages | values from per-element data; no collateral change |
| [`lh20_docs_drift`](tasks/lh20_docs_drift/REQUIREMENTS.md) | doc correction | CLI documentation | 56 tools | defaults the code computes: env vars, values filled in after parsing |
| [`lh21_data_cleaning`](tasks/lh21_data_cleaning/REQUIREMENTS.md) | data transformation | tabular data | 46 datasets | each spec's own steps, order and parameters |
| [`lh22_reconciliation`](tasks/lh22_reconciliation/REQUIREMENTS.md) | record matching | payments ledger | 50 merchants | each contract's fee, FX order, refund rule, rounding and settlement mode |
| [`lh23_experiment_audit`](tasks/lh23_experiment_audit/REQUIREMENTS.md) | statistical verdicts | A/B experiments | 50 experiments | bots, registered splits, corrected thresholds, the registered metric |
| [`lh24_contract_terms`](tasks/lh24_contract_terms/REQUIREMENTS.md) | term extraction | legal contracts | 56 contracts | amendments override; values need computing |
| [`lh25_ticket_triage`](tasks/lh25_ticket_triage/REQUIREMENTS.md) | triage routing | customer support | 80 tickets | content, customer plan, policy matrix, knowledge base, 48-hour duplicates |
| [`lh26_expense_audit`](tasks/lh26_expense_audit/REQUIREMENTS.md) | policy audit | expense claims | 56 reports | an ordered rulebook, exchange rates on each line's date, daily caps |
| [`lh27_secret_leaks`](tasks/lh27_secret_leaks/REQUIREMENTS.md) | leak detection | git history | 60 repositories | tracked or not, revoked or not, placeholders, split and encoded tokens |
| [`lh28_iam_access`](tasks/lh28_iam_access/REQUIREMENTS.md) | access decisions | IAM policies | 48 principals | explicit deny, boundaries, conditions, case-sensitive resources |
| [`lh29_fictional_calendars`](tasks/lh29_fictional_calendars/REQUIREMENTS.md) | date computation | calendar systems | 50 jobs | invented offsets, summer time, weekends and holidays no library knows |
| [`lh30_spec_validators`](tasks/lh30_spec_validators/REQUIREMENTS.md) | validator writing | identifier specs | 48 formats | each check algorithm and its parameters; graded on unseen near misses |

Fifteen tasks are graded from an answer file. The other fifteen are graded on
the workspace itself, mostly by running it: the migrated packages' tests (LH2),
the ported plugins and shared registry (LH8), the patched release lines (LH9),
the new tests against hidden mutants (LH11), fixes against the spec plus the
triage file (LH12), SQL on a hidden database (LH13), parsers on held-out logs
(LH14), equivalence and timing (LH15), ports on hidden inputs (LH16),
behaviour tests after flag removal (LH17), the container policy (LH18) and
accessibility rules (LH19) re-checked on the edited files, docs against the
parsers (LH20), exact CSV output (LH21) and validators on unseen strings
(LH30). No verifier uses an LLM judge.

The generators still take a seed, and a different seed gives a different
scenario (which units are traps, where the violations are), not only
different filler. Only seed 1 ships: one task per family, rather than several
near-copies of one.

## Layout

```
longhorizon/
  budget.py              the timeout model and the admission gate
  generators/            one module per family: generate, grade, oracle, shape, INSTRUCTION, META
    common.py            deterministic filler and helpers
  tasks/<family>/        30 Harbor task dirs, built by tools/build_longhorizon.py
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
  output for every unit** (900–2,500 tokens per unit, decoded at an assumed
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

Estimates in minutes, with a 20-minute timeout. With one subagent at a time,
every task times out:

| task | careful single | ideal single (floor) | 8 parallel subagents |
|---|---|---|---|
| lh1 | 69.5 | 27.4 | 9.9 |
| lh2 | 56.0 | 26.2 | 9.7 |
| lh3 | 45.9 | 29.6 | 7.0 |
| lh4 | 79.0 | 20.5 | 11.6 |
| lh5 | 58.0 | 23.7 | 9.6 |
| lh6 | 60.3 | 25.7 | 8.8 |
| lh7 | 59.1 | 24.0 | 8.4 |
| lh8 | 57.8 | 26.7 | 9.9 |
| lh9 | 58.0 | 24.7 | 8.6 |
| lh10 | 69.5 | 24.5 | 10.5 |
| lh11 | 52.9 | 23.7 | 8.4 |
| lh12 | 50.9 | 21.6 | 8.3 |
| lh13 | 53.1 | 23.1 | 8.5 |
| lh14 | 51.2 | 24.3 | 7.3 |
| lh15 | 50.1 | 21.3 | 8.1 |
| lh16 | 55.4 | 21.6 | 8.6 |
| lh17 | 58.2 | 21.9 | 9.2 |
| lh18 | 52.1 | 21.7 | 8.4 |
| lh19 | 51.1 | 21.5 | 8.4 |
| lh20 | 57.1 | 22.1 | 9.2 |
| lh21 | 59.6 | 22.9 | 9.2 |
| lh22 | 58.6 | 21.2 | 10.0 |
| lh23 | 61.2 | 21.9 | 10.0 |
| lh24 | 59.9 | 22.7 | 9.2 |
| lh25 | 57.9 | 23.0 | 9.6 |
| lh26 | 60.9 | 25.3 | 9.6 |
| lh27 | 61.3 | 22.3 | 10.1 |
| lh28 | 53.4 | 22.1 | 8.4 |
| lh29 | 48.0 | 22.5 | 8.7 |
| lh30 | 53.3 | 23.1 | 8.5 |

Unit sizes are **measured** from the generated workspaces. Turn latency, decode
speed and output tokens per unit are **assumptions**. Sequential subagents do
not help, so the tasks reward *parallel* delegation specifically; a test pins
this for every task.

An earlier version of this model charged turns per unit only. It overestimated
the single agent for small units, which a smart agent reads eight at a time;
the floor exists to close that gap. The gate is a real filter: it rejected LH5
until its judgement-turn estimate was corrected to match its tiny units, and
it rejected the first version of LH7 (40 locales, floor 17 min) until the
catalogue was scaled up.

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

A single agent under time pressure will look for a shortcut: one script for
every unit, a grep, trusting a label or a reported number.
`tests/test_longhorizon.py` pins that each obvious one scores below 0.75. A
passing grade should be set at 0.9. Doing nothing scores 0, except where
leaving a unit alone is sometimes right (LH9 0.41, LH17 0.38, LH20 0.51).

| task | shortcut | score |
|---|---|---|
| lh1 | call every service clean / "imports `vendor/`" means insufficient / grep for an inline check | 0.50 / 0.43 / 0.34 |
| lh2 | find-and-replace the API names | 0 of 36 packages |
| lh3 | trust raw timestamps / fix timezones, ignore skew / believe the brief | 0.10 / 0.10 / 0 |
| lh4 | trust package metadata / grep for GPL and "agent" | 0.50 / 0.61 |
| lh5 | base.yaml only | 0.49 |
| lh6 | first mechanism in the source / log keywords | 0.48 / 0.27 |
| lh7 | one generic checker (one/other plurals, byte lengths) / no errors anywhere | 0 / 0.08 |
| lh8 | parallel writers each rewrite the registry | <= 0.2 |
| lh9 | patch every vulnerable line, end-of-life too | 0 |
| lh10 | any grep hit means unsafe / grep filtered by table name | 0.20 / 0.33 |
| lh11 | smoke tests that call each function once | 0.03 |
| lh12 | call every issue fixed: without code changes / with correct code | 0 / 0.55 |
| lh13 | hard-code the visible database's numbers / right queries, UTC days | 0.04 / 0.33 |
| lh14 | right fields, timestamps and levels left as written | 0.11 |
| lh15 | one fast rewrite per function shape, variants ignored | 0.60 |
| lh16 | shell out to the original / naive ports (on their own scripts) | 0.14 / 0.40 |
| lh17 | trust the status label | 0.56 |
| lh18 | generic hardening (pin, USER, /health on 8080, drop secret-named vars) | 0 |
| lh19 | regex fixes (lang="en", alt from data attributes) | 0 |
| lh20 | regenerate tables by introspecting the parsers | 0.53 |
| lh21 | one cleaner for every dataset | 0 |
| lh22 | match by reference only / nothing to report | 0.08 / 0 |
| lh23 | naive statistics / trust every write-up | 0.34 / 0.30 |
| lh24 | base contract only, simple regexes | 0.38 |
| lh25 | keyword triage, no plan / KB / duplicate lookup | 0.39 |
| lh26 | reimburse everything at the trip-start rate | 0 |
| lh27 | a full mechanical scanner / nothing leaked | 0.27 / 0.05 |
| lh28 | evaluator without conditions or boundaries / case-folding resources / deny all | 0.08 / 0.23 / 0.04 |
| lh29 | ignore summer time / assume Sat-Sun weekends / ignore holidays / all three | 0.38 / 0.52 / 0.60 / 0.02 |
| lh30 | always valid / always invalid / right shape, any check character | 0 / 0 / 0.19 |

**These checks found real flaws.** Making the tasks distinct was also a chance
to audit them. The shortcut checks caught:

- LH16's grader accepted a "port" that ran the original shell script. It now
  runs every port under an audit hook that refuses to start a process.
- LH28 let a full evaluator that folded resource case score 0.97. Each
  principal now gets a case-sensitivity question, and grading is all or
  nothing per principal.
- LH29 let "assume Saturday-Sunday weekends" score 0.92. Its regions now have
  four weekend patterns and holidays inside the scheduling window, and
  fortnightly and quarterly jobs roll to business days.
- LH23 and LH30 each had a shortcut at 0.74. LH23 now builds most experiments
  so that the naive analysis gets them wrong, and LH30 grades each format all
  or nothing.

LH7 was replaced outright. Its earlier version (CVE reachability across
services) was a second LH1: code review of services for one rule.

## Validity threats

- **Scriptability.** A single agent that learns a family's rules and writes
  one correct script for the rest could finish in time. That script is the
  work the task asks for, so only the empirical gate can tell whether it
  happens. Units vary (rule kinds, code shapes, formats, variants, regions,
  per-unit specs) so that no generic script works. The shortcut tests catch
  only scripts that skip a rule.
- **The model is unmeasured.** Until calibration, the minute figures are only
  orders of magnitude.
- **Harness dependence.** "Parallel subagents" is a harness feature. A harness
  without them is expected to fail, and that is a finding, not a bug.
- **No network inside the container,** so the agent cannot parallelise by
  calling a model API from the shell.

## Verified so far (no model involved)

Offline, 249 tests cover distinctness, determinism, oracles, doing nothing,
shortcuts, constraints, the gate and the task layout for all 30 tasks. Every
oracle scores 1.0.

Container check: pending for this version of the 30 tasks (the previous
10 x 3 set was built and verified in Docker with no network).

In this sandbox, `apt` and `pip` inside `docker build` needed the egress
proxy, so the container check used a variant without the `apt`/`git` layer.
The committed Dockerfiles are standard.

## Ideas it takes from the 2026 literature

| from | what it adds here |
|---|---|
| OverclaimBench | lh1's REPORT.md must name services it did not fully review |
| MasDrift, "Must becomes Maybe" | lh2's frozen packages and lh9's end-of-life lines: constraints that must survive every handoff |
| CAVE-Bench (artifact vector) | lh2's false CI note |
| AbstentionBench, HANDOFF §4 | `insufficient` / `unknown` / `cannot_reproduce` is the right answer somewhere in several families |
| DecisionBench (counterfactual ceiling) | every task ships an oracle; the ceiling is 1.0 by construction |
| ClawArena-Team | execution-based grading, no LLM judge in any verifier |
