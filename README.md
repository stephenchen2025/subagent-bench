# HANDOFF

A benchmark for **subagent behavior** — what survives the delegation boundary
between an orchestrator and an isolated worker.

A subagent's product is not the work. It is *a report another agent will act on
without being able to verify it*. Existing benchmarks score end-to-end task
success, so a subagent that burns its budget and returns a vague or false report
scores the same as one that returns a precise, calibrated one — the orchestrator
recovers, and the metric never sees the difference. HANDOFF measures that
difference.

**Status:** design proposal, v0.2. Nothing is implemented yet.

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

The worked examples cover the families that carry the thesis:

- `f2_poisoned_premise_retry.json` — the brief asserts a false file path. Does
  the subagent correct its principal, or confabulate agreement?
- `f5_scope_trap_investigate.json` — the brief says *investigate*, and a tempting
  one-line fix sits in plain sight.
- `f10_handback_wrong_pushback.json` — the orchestrator pushes back, and is
  wrong. Does the subagent re-verify and hold its ground with evidence?

## Harness

The subagent runtime is not ours to write:
[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) at a pinned commit
(`DESIGN.md` §8.1). Its bash-only linear history is what makes trajectory-grounded
fabrication checking tractable in the first place. The briefs, decision probes,
frozen consumer, scorers, and effect allowlists are ours.

## Next

Milestone 1 (`DESIGN.md` §8.4) is a falsification test, deliberately: 30 tasks,
three families, one consumer, three metrics. If models with equal task
correctness do not separate on decision yield, the thesis is wrong and it is
better to learn that at 30 tasks than at 250.

It is gated on one prototype — resuming a terminated mini-swe-agent for the F10
handback turn, which mini does not currently support.
