# HANDOFF

A benchmark for **subagent behavior** — what survives the delegation boundary
between an orchestrator and an isolated worker.

A subagent's product is not the work. It is *a report another agent will act on
without being able to verify it*. Existing benchmarks score end-to-end task
success, so a subagent that burns its budget and returns a vague or false report
scores the same as one that returns a precise, calibrated one — the orchestrator
recovers, and the metric never sees the difference. HANDOFF measures that
difference.

**Status:** design proposal, v0.3. The three example tasks run against a real
fixture with programmatic checks and a validated schema. The scorers, frozen
consumer, and Harbor adapter are not built yet.

## Read this first

[**`DESIGN.md`**](DESIGN.md) — the full proposal: the measurement gap, the
evaluation unit, six metric axes, ten adversarial task families, validity
threats, and the build plan.

Three ideas carry it:

- **Capability-saturated tasks.** Every task must be ~95% solvable by the model
  under test once delegation constraints are removed. Otherwise the suite
  re-measures general agent capability instead of the delegation contract.
- **A frozen consumer.** One fixed model reads every report *in isolation* and
  answers a forced-choice decision probe. A strong orchestrator launders a weak
  subagent; freezing the consumer makes report quality attributable.
- **`INSUFFICIENT INFORMATION` as a correct answer.** Where that is the ground
  truth, an honest partial report wins and a confident complete-sounding one
  loses — which is how "knowing what you didn't establish" becomes scoreable as
  a positive rather than a penalty.

## Layout

| Path | What |
|---|---|
| [`DESIGN.md`](DESIGN.md) | the proposal |
| [`tasks/schema.json`](tasks/schema.json) | task specification schema |
| [`tasks/examples/`](tasks/examples/) | three worked task specs |
| [`envs/py_svc/`](envs/py_svc/) | the fixture repo the three tasks run against |
| [`checks/`](checks/) | effect diffing and per-task programmatic checks |
| [`tests/`](tests/) | fixture invariants and spec-consistency tests |

```bash
make install && make test    # 39 tests: spec schema, anchors, fixture invariants
```

The worked examples cover the families that carry the thesis:

- `f2_poisoned_premise_retry.json` — the brief asserts a false file path. Does
  the subagent correct its principal, or confabulate agreement?
- `f5_scope_trap_investigate.json` — the brief says *investigate*, and a tempting
  one-line fix sits in plain sight.
- `f10_handback_wrong_pushback.json` — the orchestrator pushes back, and is
  wrong. Does the subagent re-verify and hold its ground with evidence?

## Execution

Neither the runner nor the agent is ours to write.
[Harbor](https://github.com/harbor-framework/harbor) provisions a container per
task and collects traces; [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent)
is the agent inside it, already one of Harbor's built-ins (`DESIGN.md` §8.1).
mini's bash-only linear history is what makes trajectory-grounded fabrication
checking tractable at all.

Scoring runs **offline** over the artifacts Harbor emits — report, trajectory,
effect diff — rather than inside the verifier, so the task container stays
hermetic and re-scoring with a different consumer costs no agent re-runs.

## Tasks are verified, not asserted

A brief plus a probe is a sketch. Each example task ships with the fixture that
poses its problem, and every claim a spec makes about that fixture is a test:
`config/app.yaml` really is absent, late-December dates really do bucket into the
wrong year, the F10 decoy really has no importers. Specs cite evidence as
`path:line`, and those anchors are pinned, so a shifted line is caught rather
than silently mis-citing.

This is not ceremony. The first draft of the fixture failed its own invariants:
a comment in `settings/upload.yml` named the file where the retry policy really
lived, handing F2's answer to the agent before it started.

## Next

Milestone 1 (`DESIGN.md` §8.4) is a falsification test, deliberately: 30 tasks,
three families, one consumer, three metrics. If models with equal task
correctness do not separate on decision yield, the thesis is wrong and it is
better to learn that at 30 tasks than at 250.

The F10 resume problem that gated v0.2 is gone: the handback is scripted in the
task spec, not delivered by a live orchestrator, so the agent wrapper can play it
internally and the two-turn exchange fits inside a single Harbor trial.
