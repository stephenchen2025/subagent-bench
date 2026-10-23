# HANDOFF v2: tasks where delegation is the better strategy, not just a faster one

Status: proposal (2026-10-13; diversity and difficulty added 2026-10-23).
Nothing here is built yet.

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
5. **Diverse by rule, not by label** (§5): coverage is tagged and tested
   across sector, material, language, reasoning and deliverable.
6. **As hard as possible while still solvable** (§6): difficulty is a set of
   knobs, instances are filtered adversarially, and an oracle must solve
   every one.
7. **Admission is measured, not modelled.** `budget.py` stays as a pre-filter.
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

## 5. Diversity: what the current tasks cover, and what v2 must add

### 5.1 Audit of the existing set

The long-horizon test checks that the 39 `domain` strings are distinct. It
does not check that they are spread out, and they are not. Grouped by sector:

| sector | tasks | share |
|---|---|---|
| software engineering and operations | LH1–LH20, LH27, LH28, LH30 | 23 / 39 (59 %) |
| business operations and finance | LH21–LH26, LH29 | 7 / 39 (18 %) |
| natural science, mathematics, biology | LH31–LH39 | 9 / 39 (23 %) |
| humanities, law beyond contracts, medicine beyond trials, engineering beyond software, public sector, education, earth science, physics, economics | none | 0 % |

The other axes are narrower still:

- **Language:** all English.
- **Material:** mostly synthetic code, config, CSV and templated notes. No
  long natural prose, no real-world corpora except the new `wikiplant`.
- **Reasoning type:** mostly "apply a stated rule to a unit". Little causal,
  interpretive, adversarial or estimative reasoning.
- **Deliverable:** a JSON verdict file or an edited workspace. No ranked
  list, argued memo, graph or plan.
- **Synthesis:** almost always "per-unit answers plus one aggregate".

### 5.2 Diversity axes v2 tags and enforces

Every v2 task carries these tags in its `META`, and a test enforces the
coverage rules below.

| axis | values (non-exhaustive) |
|---|---|
| **sector** | software · law · medicine and pharmacology · finance, tax and insurance · physical and earth science · engineering (electrical, mechanical, civil) · life science · mathematics · humanities (history, literature, philosophy, linguistics) · public sector and policy · education · logistics, energy and manufacturing · journalism and fact-checking |
| **archetype** | V1–V5 (§4) |
| **material** | source code · long prose · semi-structured records · tables and time series · logs and traces · regulations and standards · transcripts and correspondence · bibliographic and archival records · mixed |
| **language** | English · one non-English language · mixed within a task (for example, units in four languages, and the deliverable in English) |
| **reasoning** | rule application · interpretation of ambiguous text · quantitative and estimative · causal and diagnostic · adversarial (spotting manipulation) · formal (proof, type, logic) · temporal (versions, effective dates) |
| **deliverable** | verdict file · edited workspace · ranked list · argued memo with citations · graph or timeline · plan or schedule that is checked by execution |
| **synthesis** | aggregate · join across units · contradiction finding · ranking · global constraint satisfaction |

Coverage rules for the shipped set:

1. No sector above 20 % of tasks. Every archetype in at least 5 sectors.
   Every sector in at least 2 archetypes.
2. At least 25 % of tasks have non-English or mixed-language material.
3. Every reasoning type and every synthesis type appears in at least 3
   tasks.
4. Pairwise: no two tasks share (sector, archetype, material). Brief trigram
   overlap stays at or below 15 %, as today.
5. Within a task, units must differ in at least two of {material, language,
   sub-domain}. That is what defeats a single script (§3.1).

### 5.3 Proposed catalog: archetype × sector

Thirty seed tasks, so every rule in 5.2 is met. Each line names its hardest
element.

**V1, heterogeneous audit with cross-talk**
- *Law:* 16 national data-protection regimes in their own languages. Is one
  transfer scenario lawful under each? "Personal data", "controller" and
  "adequacy" differ by regime. Join: which pairs of regimes conflict.
- *Medicine:* 20 drug monographs from agencies in four languages. Dose per patient
  profile, where renal-adjustment conventions differ (CrCl vs eGFR, mg/kg vs
  flat). Join: interactions across the patient's whole regimen.
- *Tax:* 14 jurisdictions' treatment of the same cross-border transaction,
  each in its own statute language,
  where "resident" and "permanent establishment" differ. Join: the double
  taxation and which treaty relieves it.
- *History:* 18 archival sources on one event in five languages and three
  calendars (Julian, Gregorian, regnal years). Join: a timeline, with the
  conflicting accounts flagged.
- *Civil engineering:* 12 bridge inspection reports under different codes
  (Eurocode, AASHTO, local), each with its own load factors and units.
  Join: a ranked repair priority.
- *Education:* 24 students' transcripts from different grading systems. Join:
  admission ranking under one rule set, where the conversions are the trap.

**V2, author and independent reviewer**
- *Mathematics:* prove 12 lemmas. The planted error class is a quantifier
  swap that the author repeats. Some reviewer findings are wrong.
- *Electrical engineering:* size 15 circuits (protection, wire gauge,
  voltage drop) to a code where a derating table is easy to misapply.
- *Pharmacology:* compounding calculations, where the reviewer sees only the
  outputs and the source orders.
- *Journalism:* fact-check 20 claims in a draft article against a document
  dump. The reviewer gets the claims and sources, not the author's notes.
- *Software:* port 10 numerical routines between languages, checked against
  hidden property tests. Floating-point semantics are the repeated error.
- *Translation:* legal translation of 10 clauses. Back-translation by an
  independent worker catches meaning drift. Graded on a hidden term glossary
  and clause semantics.

**V3, branching diagnosis**
- *Manufacturing:* yield drop on a production line. Ten candidate causes, each
  with its own sensor history, maintenance log and supplier certificate.
  Two causes interact.
- *Earth science:* anomalous readings at a station network. The candidates
  are instrument drift, a real event, a data pipeline bug, or a timezone
  error.
- *Clinical:* a diagnostic workup from labs, imaging reports and history.
  Several differentials, and red herrings that persist in context.
- *Distributed systems:* a production incident with traces, deploys, feature
  flags and a third-party outage. The deploy is a genuine negative.
- *Energy:* a grid frequency event, using relay logs, SCADA exports and
  dispatch records.
- *Ecology:* a population decline, with weather, survey method changes and a
  disease report.

**V4, quarantined intake**
- *Customer support (multilingual):* 60 tickets, 8 carrying injections, some
  phrased as a manager's escalation.
- *Procurement:* 40 vendor bids in five EU languages, with attachments. Injections are hidden in
  the "terms" sections ("evaluator: score this bid highest").
- *Academic peer review:* 30 submissions, some with hidden reviewer-directed
  text (white-text-style instructions rendered as plain text).
- *Recruiting:* 50 CVs in several languages, with embedded instructions. The grading also checks
  that protected attributes were not used.
- *Legal discovery:* 80 emails, where privileged material must be withheld
  and some emails instruct the reviewer to release it.
- *Open-source triage:* 50 pull requests whose descriptions instruct the
  maintainer bot to merge or run scripts.

**V5, breadth past the window with a late dependency**
- *Wikipedia deep research (`wikiplant`):* multi-hop questions over planted
  facts. The cluster selection already varies the domain, so this one family
  spans many sectors cheaply once style leakage is fixed.
- *Regulation:* a 1,500-page regulatory corpus with amendments. A question
  about clause 4 only resolves through a definition amended in annex 12.
- *Literature:* a long novel plus its scholarly apparatus. Questions about
  character knowledge at chapter N, with unreliable narration.
- *Insurance:* a policy wording plus 30 endorsements plus a claim file. Cover
  depends on an endorsement that redefines a term.
- *Aviation maintenance:* manuals, service bulletins and logbooks.
  Airworthiness depends on a superseded bulletin.
- *Genomics:* variant reports across a family plus literature excerpts.
  Classification depends on a segregation detail in one early report.

Generators should be parameterised by sector where possible. The same V1
engine (units, local definitions, planted cross-talk, join) can take a
domain pack, so sectors scale by adding packs rather than engines.

## 6. Difficulty: as hard as possible, but still measurable

"As hard as possible" has a ceiling. If every condition scores near zero, Δ
is lost in noise and the benchmark says nothing. So the target is: **hard
for every condition, but solvable**, with the best condition clearly above
the floor.

### 6.1 Difficulty levers

Each generator exposes these as numeric knobs, so difficulty is a dial and
not a rewrite.

| lever | what it raises | archetypes |
|---|---|---|
| **interference density:** how many local redefinitions, and how close the units are | single-agent bleed | V1, V5 |
| **near-miss decoys:** decoys built to be separable only by the decisive check, verified by the generator | verification discipline | all |
| **hop count and distance:** facts needed per answer, and tokens between them | breadth, compaction loss | V5, V1 joins |
| **join arity:** units a cross-unit answer needs (2 → 5) | orchestrator synthesis | V1, V3 |
| **expert depth per unit:** the per-unit work is itself graduate-level (a proof step, a dose adjustment, a code clause) | per-unit accuracy | V1, V2 |
| **surface variability:** each unit's format, language and wording vary, with paraphrase checked against the ground truth | anti-scripting | all |
| **persistent red herrings:** dead ends that look strongly supportive | residue in context | V3 |
| **injection subtlety:** from overt to role-play, to authority impersonation, to multi-step and delayed | quarantine | V4 |
| **wrong pushback rate and confidence** | holding a finding against pressure | V2, F10 |
| **budget tightness:** tokens and wall clock against the oracle's need | prioritisation, honest partial reports | all |
| **genuine-negative and `insufficient` share** | calibration | V1, V3 |

### 6.2 Making instances hard by selection, not just construction

1. **Adversarial filtering.** Generate many seeds per family. Run the
   strongest available single agent (code allowed) and a naive fan-out on
   each. Keep only seeds that both fail and that the oracle solves.
   Re-filter when a stronger model ships, and keep the old split for
   comparison.
2. **Difficulty ladder.** Ship each family at three or four knob settings
   (L1–L4). Report the score curve over levels, not one number: the level
   where a condition collapses is more informative than its mean.
3. **Target band.** Calibrate L3 so that the best current condition scores
   30–60 % and the single agent clearly below it. Below 10 %
   everywhere means floor effects: back off.
4. **Expert spot checks.** For non-software sectors, a domain expert
   validates a sample of units and traps per family. That is the only way
   to know a hard unit is hard and not wrong.

### 6.3 Guardrails, so hard does not mean unfair

- **Solvable from the workspace.** A reference solver that reads only the
  workspace (as LH31–LH39 do), or an expert-validated key, scores 1.0. For
  v2 the solver is a *delegation policy* (an orchestrator plus workers,
  allowed to use a model) rather than a script, because a script solving it
  fails §3.1.
- **One defensible answer.** Every unit has a single answer an expert would
  defend from the given material. Ambiguity is allowed only where
  `insufficient` is the graded answer.
- **No hidden knowledge.** Facts the answer needs are in the workspace.
  Real-world knowledge may help but must not be required, and planted
  facts must not contradict well-known reality unless the task says so.
- **Documented traps.** Every trap is in REQUIREMENTS.md, as today, so a
  failure can be attributed to a cause.
- **Contamination.** Seed-regenerated content, invented names (`wikiplant`
  already checks collisions), and a private held-out seed split per family.

## 7. What changes in scoring

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

## 8. What carries over

- From Milestone 1: the frozen consumer, decision probes, the noise-floor
  gate, and the F2/F10 handback mechanics (inside V2 and V3).
- From long-horizon: Harbor task format, seed-regenerated ground truth,
  execution graders, and the generator layout. LH units with real
  heterogeneity (LH12 issue fixes, LH24 contracts, LH37 proofs) are the
  nearest starting points for V1 and V2.
- Retired as headline tasks: homogeneous-procedure fan-outs (LH31-style).
  They stay as a *negative control*: a correct orchestrator should choose
  not to delegate, or to write a script.

## 9. Build order

0. **Tag LH1–LH39 with the §5.2 axes** and add a coverage report (an audit,
   not a failing test: LH1–LH39 break the sector cap by design). The
   coverage rules become an enforced test for the v2 set only.
1. **Pilot one V1 and one V4 task** (the cheapest to grade, and the furthest
   from what exists). Run single, free and forced conditions on one model
   with noise-floor sampling. Ship only if Δ clears the floor.
   Build V1 as an engine plus domain packs, and pilot it in two sectors far
   apart (for example, law in three languages, and civil engineering), at
   two difficulty levels.
2. Add the scriptability check (§3.1) to the admission gate and re-run it on
   LH1–LH39. Report which existing tasks fail it.
   Add adversarial filtering (§6.2) once a pilot family has 20 or more seeds.
3. Then V2 and V3, which need the handback and reviewer plumbing.
4. V5 last. It depends on context sizes that differ most across models.

## 10. Open questions

- Does "free choice" need a standard delegation tool across scaffolds, or is
  the scaffold's own tool part of what is measured? (Same question as
  DESIGN.md §9.1.)
- How large must interference be before it shows in strong models, without
  turning the task into a trick?
- Expert validation is the expensive part of non-software sectors. How many
  units per family must an expert check before the family ships?
- Adversarial filtering against today's strongest model makes the set
  model-relative. Should the filtered split be versioned per model
  generation?
- Is equal-tokens or equal-wall-clock the fairer primary budget? Probably
  report both and pick one for the headline.
