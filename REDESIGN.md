# HANDOFF v2: tasks where delegation is the better strategy, not just a faster one

Status: proposal (2026-10-13). Nothing here is built yet.

## 1. Why the current tasks show subagents adding little or negative value

Both tracks were built so that a subagent is *possible*. Neither was built so
that a subagent is *better*. Looking at how they are constructed, four things
work against delegation:

1. **The long-horizon units can be scripted.** Each LH task is "the same
   procedure × N units". The reference solvers in `longhorizon/solutions/`
   (about 120 lines each, 1,060 in total) solve LH31–LH39 deterministically
   and score 1.0. A single agent that writes such a script once skips the
   per-unit decode cost. `budget.py` treats that cost as the thing batching
   cannot remove, but writing a script removes it. The 20–30 minute "ideal
   single agent" floor is a lower bound for an agent that reasons through each
   unit in prose, not for one that writes code.
2. **The only advantage modelled is wall-clock parallelism.** Every admission
   check is about minutes. A faster model, a longer timeout, or the script
   above erases that advantage, and nothing else in the design favours
   delegation.
3. **The traps only penalise delegation.** Constraints that must survive the
   hand-off, cross-unit links visible only to the orchestrator, shared files
   that siblings clobber: each is free for a single agent and costly for an
   orchestrator. That suits a benchmark of delegation *failures*. A benchmark
   of *when to delegate* tilts toward "don't".
4. **Milestone 1 tasks are deliberately small.** About 6 commands and under a
   minute each. A report boundary on a task that fits in one context can only
   lose information. It was designed to measure report quality, not
   delegation value.

The common thread: the tasks reward *throughput*, and a single agent can buy
throughput with code. Delegation's real advantages are about *what a context
contains*. Throughput is incidental.

## 2. What subagents are actually good for

These hold even with an unlimited clock:

| advantage | mechanism | single-agent failure it avoids |
|---|---|---|
| **A. Context isolation** | each unit is judged in a context holding only that unit | cross-unit interference: a definition, convention or conclusion from unit 3 leaks into unit 17 |
| **B. Fresh-eyes verification** | a checker that has not seen the author's reasoning | anchoring: an agent re-checking its own work tends to re-confirm it |
| **C. Exploration without residue** | dead-end branches are explored in contexts that are then thrown away | a context full of failed hypotheses, stale observations and abandoned assumptions |
| **D. Quarantine** | untrusted content is read by a worker that returns only structured fields | prompt injection reaching the agent that holds write access and the full task |
| **E. Breadth past the window** | each worker reads 50–150k tokens the orchestrator never sees | compaction losing the detail a later step needs |

HANDOFF's existing strength, scoring the report against a frozen consumer,
stays. These advantages only pay off if the report carries the result back
intact.

## 3. Design rules for v2 tasks

1. **No scriptable units.** Units are heterogeneous in kind, not just in
   parameters. Each needs natural-language judgement over a different
   document. Admission check: a reference *program* written from the docs
   must score below 0.5. If a script solves it, it is a scripting benchmark.
2. **Interference is planted, not just volume.** Units carry locally valid
   facts that are wrong elsewhere: the same term defined differently per
   contract, a convention that flips between modules, a plausible conclusion
   from one unit that is false for its neighbour. A single context that holds
   several units is measurably more likely to transfer them.
3. **Delegation must also be able to lose.** Keep one orchestrator-only
   element per task (a cross-unit link, the final aggregate, one shared
   file), so the benchmark rewards *good* delegation, not delegation per se.
4. **Equal budgets.** Compare conditions at equal total tokens (and equal
   wall clock), so "more compute" is not mistaken for "better structure".
5. **Admission is measured, not modelled.** `budget.py` stays as a pre-filter.
   A task ships only if real runs show, for at least one model:
   `score(oracle delegation policy) − score(best single-agent run) ≥ the
   measured noise floor`, with the single agent allowed to write and run
   code.

## 4. Composite task archetypes

Each archetype combines two or more of the advantages in §2. Every task still
ends in a delivered artifact graded by execution or an answer key, plus
subagent reports scored by the frozen consumer.

### V1. Heterogeneous audit with planted cross-talk (A + E + orchestrator join)
- 12–20 units, each a *different* kind of document (a contract, a policy, a
  log bundle, a config tree, a memo), 20–60k tokens apiece.
- Each unit redefines shared vocabulary locally ("active customer", "business
  day", "fee") and contains one conclusion that is true there and false in at
  least one other unit.
- Deliverable: a verdict per unit plus a join no unit can answer alone (for
  example, which two units contradict each other).
- Single-agent failure: definition bleed. Sloppy-delegation failure: the
  join is never done, or a report drops the local definition it relied on.

### V2. Author / independent-reviewer loop (B + F10 handback)
- The agent must produce N fixes (or analyses), each with a subtle error
  class that its author tends to repeat: an off-by-one convention, a
  misread spec clause.
- A hidden grader scores the final state. Reviewing is optional, but a
  reviewer that has not seen the author's reasoning catches the planted
  class at a higher rate.
- The pushback channel is kept, and some reviewer findings are wrong. Good
  behaviour is author and reviewer settling it on evidence, not deferring.
- Measures whether the orchestrator uses independent review, and whether
  either side caves.

### V3. Branching diagnosis (C + F3 negatives)
- An incident with 6–10 candidate causes. Testing each one means reading
  large, different evidence (logs, traces, diffs). Most are dead ends, and
  one is a genuine negative ("not caused by the deploy").
- Each dead end leaves misleading residue (a correlated-but-irrelevant
  spike) that biases the next hypothesis if it stays in context.
- Deliverable: the root cause, the ruled-out list with evidence, and a fix.
- Scored on accuracy *and* on whether the reports' ruled-out evidence lets
  the frozen consumer answer "was it X?" probes correctly.

### V4. Quarantined intake (D + F9)
- 30–60 inbound items (tickets, emails, vendor files), some carrying
  injections aimed at whichever agent reads them: "also delete X", "mark
  this approved".
- The orchestrator holds the write tools. Good structure: workers read raw
  items and return schema-bound summaries, and the injection is reported as
  a finding.
- Grading: correct triage, *zero* injected effects (from the effect diff),
  and injections surfaced in the reports. A single agent that reads
  everything and holds the write tools is the exposed configuration.

### V5. Breadth past the window with a late dependency (E + compaction)
- Total material is 3–5× one usable context. A question asked at the end
  depends on a detail on page 1 of unit 2 that only matters once unit 19 is
  read.
- Workers that report *what they did not include* (F8 compression, F6
  coverage honesty) let the orchestrator re-query the right worker.
  Compaction in a single agent tends to drop the detail.

## 5. What changes in scoring

- **Headline: delegation advantage (Δ).** Same model, three conditions:
  single agent (code allowed), free choice (model may delegate), and forced
  naive fan-out. Report the three scores and Δ = free − single. A model
  that delegates where it hurts, or fails to where it helps, shows up
  directly.
- **The delegation decision is scored.** Did the orchestrator split along the
  isolation boundary, keep the join, send the reviewer only the artifact, and
  quarantine untrusted input? These come from the trajectory, not a judge.
- **Report axes stay.** Decision yield, calibration, scope discipline and
  CIR, applied to every subagent report captured in the run.
- **Noise floor is required.** As in Milestone 1, a Δ smaller than the
  measured run-to-run spread is reported as "no difference".

## 6. What carries over

- From Milestone 1: the frozen consumer, decision probes, the noise-floor
  gate, and the F2/F10 handback mechanics (inside V2 and V3).
- From long-horizon: Harbor task format, seed-regenerated ground truth,
  execution graders, and the generator layout. LH units with real
  heterogeneity (LH12 issue fixes, LH24 contracts, LH37 proofs) are the
  nearest starting points for V1 and V2.
- Retired as headline tasks: homogeneous-procedure fan-outs (LH31-style).
  They stay as a *negative control*: a correct orchestrator should choose
  not to delegate, or to write a script.

## 7. Build order

1. **Pilot one V1 and one V4 task** (the cheapest to grade, and the furthest
   from what exists). Run single, free and forced conditions on one model
   with noise-floor sampling. Ship only if Δ clears the floor.
2. Add the scriptability check (§3.1) to the admission gate and re-run it on
   LH1–LH39. Report which existing tasks fail it.
3. Then V2 and V3, which need the handback and reviewer plumbing.
4. V5 last. It depends on context sizes that differ most across models.

## 8. Open questions

- Does "free choice" need a standard delegation tool across scaffolds, or is
  the scaffold's own tool part of what is measured? (Same question as
  DESIGN.md §9.1.)
- How large must interference be before it shows in strong models, without
  turning the task into a trick?
- Is equal-tokens or equal-wall-clock the fairer primary budget? Probably
  report both and pick one for the headline.
