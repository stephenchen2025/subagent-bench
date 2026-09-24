# The orchestrator track: does delegating actually pay?

HANDOFF (DESIGN.md) scores the **worker**: given a brief, is the report a
subagent returns worth acting on? This track scores the **orchestrator**: given a
task and a subagent tool, does the agent delegate when delegation pays, avoid it
when it doesn't, and how much of the available benefit does it actually capture?

The design target is a specific shape of result:

- **Without subagents, the metric is flat.** A solo agent's delegation metrics
  are zero by construction. On delegation-favourable tasks its score stops rising
  (or falls) as the task grows, because it runs into a per-agent resource wall.
- **With subagents, the benefit is visible and attributable.** Lift over solo,
  a compute-matched control that separates *structure* from *more tokens*, and a
  scripted-decomposition ceiling that shows how much **headroom** is left.
- **Where subagents hurt, that shows too.** Tasks where delegating costs more
  than it returns carry an over-delegation tax, so "always fan out" does not win.

Everything here is programmatically verified. No LLM judge, no frozen consumer:
each task writes an answer or a code change, and a verifier with the ground truth
grades it. That keeps the track cheap to run and easy to share.

---

## 1. What the field says about when to delegate

Summarised from the sources in §9. Each rule is traced to the task family that
tests it (§3).

### When subagents help

| Condition | Why | Evidence | Family |
|---|---|---|---|
| **Breadth**: many independent items, each needing to be read | Each worker gets a fresh window; only the distilled result returns. The lead's context is spent on synthesis, not raw material. | Anthropic's research system: multi-agent beat single-agent Opus by 90.2% on breadth-first queries, and token use alone explained ~80% of the variance. | **W** wide sweep |
| **Independent multi-step investigations** | Per-item work is sequential; items are not. Parallel workers cut the critical path. | Anthropic: parallel subagents cut research time by up to 90%. Google/MIT scaling study: centralized coordination +80.9% on parallelizable tasks. | **P** parallel probes |
| **Noisy intermediate output** | Verbose logs and test output stay in the worker's context; the lead receives a summary. Context rot degrades every frontier model as input grows. | Claude Code docs ("use a subagent when the task produces verbose output you don't need"); Chroma context-rot study (18 models, all degrade). | W, P and C, via per-observation truncation and the context cap |

### When subagents hurt

| Condition | Why | Evidence | Family |
|---|---|---|---|
| **Coupled subtasks with implicit shared decisions** | Isolated workers make independent choices about things the brief didn't pin down. Each is locally reasonable; together they are incompatible. | Cognition, "Don't Build Multi-Agents" (the Flappy Bird example). MAST: 37% of multi-agent failures are inter-agent misalignment, 42% are specification problems. | **C** coupled views (without a contract) |
| **Sequential tasks** | Each step needs the previous step's result, so there is nothing to run in parallel; splitting only adds briefs, cold starts and handoffs that can go wrong. | Scaling study: on sequential tasks every multi-agent variant *degraded* performance by 39–70%. Claude Code docs: work where "multiple phases share significant context" belongs in the main conversation. | **L** ledger chain |
| **The benefit is just compute** | A multi-agent system that wins only because it spent more tokens has shown nothing about structure. | "Rethinking the Value of Multi-Agent Workflow": a single agent matches homogeneous multi-agent workflows. Anthropic: 15× the tokens of chat. | the **solo-xl** control (§4) |

### What a good orchestrator does once it delegates

These are the process behaviours the diagnostics (§5.3) look for:

1. **Scale effort to the task.** Anthropic's rule of thumb is one agent for
   simple fact-finding, 2–4 for comparisons, 10+ only for broad research.
   Spawning 50 subagents for a simple query is a documented failure.
2. **Partition cleanly.** Cover every item exactly once. Duplicated work and
   gaps were both observed failure modes in Anthropic's system.
3. **Write self-sufficient briefs.** Each brief needs an objective, an output
   format, tool guidance and explicit boundaries (Anthropic). For coupled
   work, the brief must carry the shared contract (Cognition).
4. **Keep state in one loop.** Workers are stateless, narrowly scoped, and
   read-mostly. The lead owns decisions and writes (Cognition's revised position;
   the Claude Code guidance to parallelise research, not edits).
5. **Synthesise without loss.** A finding a worker reported and the lead
   dropped is pure waste. That loss is measurable here.

---

## 2. Unit of evaluation

A **run** is one (task, model, condition) triple. Every run produces:

```
reward.json      verifier: score in [0,1] plus sub-scores   (Harbor, scaffold-agnostic)
telemetry.json   who spawned what, when, with which brief; per-agent tokens,
                 steps and peak context; worker reports; wall-clock
```

Reference-harness runs write `telemetry.json` directly. For any other scaffold
(Claude Code, Codex CLI) it is reconstructed from Harbor's ATIF trajectory:
subagent calls are tool calls, and Claude Code marks worker steps
`is_sidechain`. `orch/atif.py` does the conversion.

## 3. Task families

Every task is **long-horizon with an explicit breakdown**, and a test enforces
it (`test_every_task_is_long_horizon_with_an_explicit_breakdown`): a scripted
agent with perfect reading and unlimited context needs 60–160 steps, and there
are at least 8 units of work. Real agents need more. Every family is a
procedural generator (one seed, one new variant), and every family has a
**size** knob, because the delegation question is about scale.

| Family | Units, and how they split | Label | Sizes | Verifier |
|---|---|---|---|---|
| **W — wide sweep.** Find every support ticket reporting a real duplicate charge and name the order. Positives are paraphrased and decoys share their vocabulary, so grep narrows the work but cannot finish it. | one file per ticket in `tickets/`; any grouping works | `delegate` | N ∈ {60, 96, 128} | F1 over (ticket, order) pairs |
| **P — parallel probes.** Diagnose K degraded services, three dependent `svcctl` calls each (status → component → logs), naming the failing component and root cause. | services named in the instruction; each is independent | `delegate` | K ∈ {15, 25, 38} | per-service (component, cause) accuracy |
| **C — coupled views.** Add job priorities, then make each of M views show them exactly as its own spec in `docs/views/` says. | views named in the instruction; each is independent *once the record format is fixed*, which the instruction deliberately leaves open | `delegate`, behind a contract | M ∈ {20, 30, 40} | hidden checks: core behaviour + one per view |
| **L — ledger chain.** Follow H ledger pages; each page's rule picks the next. Decoy pages outnumber the chain. | hops, strictly sequential: page k+1 is unknown until page k is read | `solo` | H ∈ {60, 100, 140} | correct prefix of the visited path |

Measured minimum solo effort (scripted perfect agent, unlimited context, seed 1):

| | smallest | middle | largest | hits the 32k context wall |
|---|---|---|---|---|
| W steps / context | 69 / 64k | 113 / 104k | 144 / 132k | at every size |
| P steps / context | 61 / 21k | 101 / 37k | 153 / 61k | from K=25 |
| C steps / context | 65 / 20k | 95 / 29k | 125 / 38k | at M=40 (real agents sooner) |
| L steps / context | 64 / 6k | 106 / 10k | 148 / 15k | never, by design |

So W, P and C all have a solo curve that falls as the task grows, and L has
nothing for a subagent to buy. C is the family that separates good delegation
from bad: any one consistent record format scores 1.0, but workers choosing
independently average about 0.3.

Every task ships a `solution/solve.sh`, so `harbor run -a oracle` proves the
task is solvable and its verifier returns 1.0. A task that fails that check
does not ship. A system-track run against a scaffold with a 200k or 1M window
needs larger sizes; the generator takes any size
(`tools/orch_generate.py --sizes W=60,128,256 --out build/orch-big`).

## 4. Conditions

The benefit of subagents is a *difference*, so every task is run under matched
conditions. Holding the model, tools and task fixed, only the delegation
affordance changes.

| Condition | Subagent tool | Per-agent context | Purpose |
|---|---|---|---|
| **solo** | no | 1× | the flat baseline |
| **solo-xl** | no | 8× context and steps | compute-matched control. If delegate beats solo-xl, the gain is structural (isolation and parallelism), not just more tokens. If it doesn't, say so. |
| **delegate** | yes, model decides | 1× each | the system under test |
| **oracle-split** | scripted by the harness | 1× each | the ceiling: an ideal partition, ideal briefs and scripted synthesis, with the same model as workers. Defined for W, P and C (C's plan puts the record contract in every brief). |

For L the ideal policy is *not to delegate*, so its ceiling is the solo score
and the interesting numbers are the tax and the decision.

In the system track (Claude Code under Harbor), `solo` is
`--ak disallowed_tools=Agent,Task` (current and older names of the tool) and
`delegate` is the default tool set. solo-xl
and oracle-split are reference-harness only.

## 5. Metrics

### 5.1 Outcome: benefit and headroom

For delegation-favourable families (W, P), per model and per size:

```
Lift              = S(delegate) − S(solo)          what subagents bought
Structural lift   = S(delegate) − S(solo-xl)       what they bought beyond compute
Headroom          = S(oracle-split) − S(delegate)  orchestration left on the table
Worker headroom   = 1 − S(oracle-split)            worker skill left on the table
Capture           = Lift / (S(oracle-split) − S(solo))
```

**Capture** is the headline. It is 0 for a solo agent *by construction* (the
flat line), 1 for an orchestrator that matches the scripted ideal, and negative
for one that delegates badly enough to do worse than going alone. It is undefined
when the ceiling is less than 0.05 above solo; small tasks carry no signal and
are excluded rather than divided by noise.

### 5.2 Cost of delegating where it doesn't pay

For L:

```
Over-delegation tax = S(solo) − S(delegate)       (≥ 0 is a loss)
Cost ratio          = tokens(delegate) / tokens(solo)
Delegation rate     = fraction of runs that spawned anything
```

The cost ratio includes the price of *carrying* the affordance: the delegate
prompt documents the `subagent` command, so a lead that never spawns still pays
a few hundred tokens per call for it (the rehearsal's judicious policy shows
1.04× on L without spawning once). Claude Code's Agent tool description
costs the same way. That is a real cost of offering subagents, so it stays in.

**A caveat the rehearsal surfaced.** On L, a relay of workers (each continuing
where the last stopped) scores 1.00 *and* costs fewer tokens than solo (0.31×):
a solo agent re-reads its ever-growing context on every step, while each relay
worker's context stays short. Scripted workers never fumble a handoff, so in
the rehearsal splitting a sequential task costs nothing. Whether real handoffs
lose the thread, as the scaling study found, is exactly what a live run on L
measures. Decision accuracy still counts delegating on L as the wrong call,
since there is no parallelism to gain; the tax and cost columns show whether
that judgment is right for a given model.

**Harm** covers what capture cannot see. Capture skips cells where solo is
already at the ceiling (e.g. C at M=20), so a delegate that scores *below*
solo there would vanish from it. Harm is the mean of max(0, solo − delegate)
over every delegation-favourable cell.

### 5.3 Judgment and process (delegate runs, from telemetry)

| Metric | Definition |
|---|---|
| **Decision accuracy** | Balanced accuracy of "spawned ≥1 subagent" against the task label, over tasks labelled `delegate` or `solo`. |
| **Fan-out** | subagents spawned, peak concurrency |
| **Coverage** | fraction of the task's work items (tickets, services, views) named in at least one brief |
| **Duplication** | fraction of named items that appear in more than one brief |
| **Synthesis loss** | items a worker reported correctly that the final answer lacks or gets wrong |
| **Lead context peak** | the orchestrator's peak context as a fraction of its cap. Delegation should keep it low. |
| **Cost** | total tokens (lead + workers), lead tokens, wall-clock, critical path |

Coverage and duplication need the item ids, which every W, P and C task exports
as `work_items`. Synthesis loss needs worker reports, which both the reference
harness and Claude Code transcripts preserve.

### 5.4 Headline table

Per model, one row per condition, with columns for each family and size,
Capture, harm, tax, decision accuracy, and total tokens. The required plot is score
against task size, one line per condition. The area between solo and delegate
is the benefit; the area between delegate and oracle-split is the headroom.

## 6. Reference harness

mini-swe-agent (bash-only, linear history) extended with one pseudo-command,
intercepted by the harness before it reaches the container:

```bash
subagent spawn <<'EOF'        # start a worker in the background; prints its id
<brief>
EOF
subagent wait [id ...]        # block until workers finish; prints their reports
subagent run <<'EOF'          # spawn and wait for one
<brief>
EOF
```

Several `spawn`s can go in one command, which is how the model expresses
parallelism. Workers share the container's filesystem, as Claude Code's
subagents do, but have their own context and step budget. They cannot spawn
further workers (depth 1), and they return a delimited report, reusing HANDOFF's
worker contract.

Per-agent limits are explicit and identical for the lead and each worker:

| Limit | Default | Why |
|---|---|---|
| context | 32k tokens | the wall a solo agent hits. Enforced by counting before every model call; exceeding it ends that agent, and whatever it already wrote to disk is scored. |
| steps | 160 | enough for a solo agent to run the whole horizon, so the binding wall is context, not an arbitrary turn cap |
| observation | 16k chars | head+tail truncation, as real scaffolds do. Stops `cat *` from being a free escape hatch. |
| subagents | 8 concurrent, 16 total | |

Every observation ends with a `[context: 12.3k / 32k tokens]` footer in every
condition, so an agent can plan around its own limit.

The limits are the experiment's controlled variable, not a hidden trick, and
they are stated in `task.toml` metadata. The system track swaps them for the
scaffold's real ones.

## 7. Validity threats

- **The cap is doing the work.** Partly true: a finite window is *why*
  delegation helps. The mitigation is solo-xl. The report must say whether
  delegate beats it, and if not, the honest reading is "subagents bought
  compute, not structure". Context rot is the mechanism that would let
  delegate win even against solo-xl; this track can measure it and does not
  assume it.
- **grep beats reading.** W is built so keyword search narrows the search but
  cannot settle it (decoys share every keyword; positive cases are paraphrased).
  A test checks that the best keyword classifier stays well below ceiling on
  generated sets.
- **Batching beats delegating on P.** A solo agent can run all K status
  calls in one command. The 16k observation cap makes that lossy at high K, but
  it remains a legitimate strategy, and a strong solo baseline is the point.
- **Scaffolds differ.** Claude Code auto-compacts, so in the system track
  delegate vs solo measures subagents against compaction, not against a hard
  wall. That is still the question a practitioner asks, but it is a different
  question and is labelled as such.
- **Latency is noisy.** Wall-clock is reported, never used as the score.

## 8. Status, and what has been verified

**Built:** four generators (W, P, C, L), a stdlib-only in-container verifier,
Harbor emission with oracle solutions, the reference harness with all four
conditions, a Harbor agent for it, ATIF import for any other scaffold, the
metrics, the report, and a scripted-policy rehearsal. The task set is checked in
as `datasets/orch-v0.2` (36 tasks: 4 families × 3 sizes × 3 seeds); v0.1's
short tasks and the S family were retired because they were not long-horizon.

**Verified against real Harbor 0.23.0 in Docker, with no API key:**
`harbor run -a oracle` over the full set: all 36 tasks build, run their oracle
solution, and score 1.0 (`results/harbor-oracle.md`). The reference harness then ran all
six scripted policies over the set inside Docker (`-a
orch.harbor_agent:OrchRehearsalAgent`, the lead and up to 8 parallel workers in
one container). The 216 trials match the local rehearsal in every one of the 72
(condition, family, size) cells (`results/rehearsal-harbor/`).

**The rehearsal.** Every agent is a scripted *perfect reader*, so reading skill is
held constant and only structure varies. That checks that the metrics separate
policies as designed (`make orch-rehearse`, 3 seeds, 216 runs, ~3 minutes;
`results/rehearsal-local/`):

| delegate policy | capture | harm | tax L | decision acc. | coverage | duplication | synthesis loss |
|---|---|---|---|---|---|---|---|
| judicious: delegates W, P and C with the contract; follows L itself | 1.00 | 0.00 | 0.00 | 1.00 | 1.00 | 0.00 | 0.00 |
| eager: delegates everything finely, no contract; relays L | 0.52 | 0.22 | 0.00 | 0.50 | 0.93 | 0.00 | 0.00 |
| sloppy: gaps, duplicate groups, drops findings | −0.10 | 0.15 | 0.00 | 1.00 | 0.87 | 0.20 | 0.50 |

Solo falls with size on every splittable family (W 0.61 → 0.40, P 1.00 → 0.58,
C 1.00 → 0.84), each time on `ContextExceeded`. On C, fanning out without the
contract averages about 0.3 even where solo is perfect, which is what the harm
column exists to catch. Structural lift is exactly 0 everywhere, because a
perfect reader has no context rot, and L shows no tax because scripted relays
never fumble a handoff (§5.2). Both are questions only a real model can answer.

**Next:**

1. **First real run** with a cheap model (Haiku 4.5; needs `ANTHROPIC_API_KEY`):
   4 conditions × 36 tasks = 144 runs. `make orch-run
   MODELS=anthropic/claude-haiku-4-5-20251001` locally, or Harbor as in the README.
2. **System track:** Claude Code with and without the Agent tool on the same set;
   `orch_collect` reads its ATIF trajectories.
3. **Link the tracks:** score delegate-condition worker reports with HANDOFF's
   frozen consumer, to tell whether synthesis loss comes from bad reports or from
   a bad lead.

## 9. Sources

- Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- Claude Code docs, [Subagents](https://code.claude.com/docs/en/sub-agents)
- Cognition, [Don't Build Multi-Agents](https://cognition.com/blog/dont-build-multi-agents)
- Kim et al., [Towards a Science of Scaling Agent Systems](https://arxiv.org/abs/2512.08296) ([Google Research summary](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/))
- [Rethinking the Value of Multi-Agent Workflow: A Strong Single Agent Baseline](https://arxiv.org/abs/2601.12307)
- Cemri et al., [Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) (MAST)
- Chroma, context rot; Liu et al., *Lost in the Middle* (TACL 2024), via [this summary](https://www.morphllm.com/context-rot)
