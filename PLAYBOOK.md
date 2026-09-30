# Playbook: running the benchmark

A step-by-step runbook for a person or an agent running HANDOFF on their own
machine. Each play says what it needs, what to run, how long it takes, what
"done" looks like, and what to commit. Run the plays in order; each one is
resumable, so an interrupted run is restarted with the same command.

| play | what it answers | needs | time |
|---|---|---|---|
| 0. Setup | -- | Python 3.11+, git | minutes |
| 1. Finish the Gemma pilot | does the whole Milestone 1 pipeline work on real models? | a Gemini API key (free tier) | about a day of throttled running |
| 2. Milestone 1 for real | do models with equal task success differ in report quality? | an Anthropic API key | hours |
| 3. Check the long-horizon tasks | are the 39 tasks buildable, solvable and fair? | Docker, uv | about 15 minutes |
| 4. Calibrate the long-horizon track | does one agent time out while parallel subagents finish? | Docker, uv, a model API key | hours to days |

State when this playbook was written: the Gemma pilot has **14 of 60**
episodes in `results/milestone1-pilot-gemma/`; Milestone 1 with Claude has 18
of 60, unscored, in `results/milestone1/`; no model has run a long-horizon
task yet.

---

## 0. Setup

```bash
git clone https://github.com/stephenchen2025/subagent-bench && cd subagent-bench
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
make test          # all tests should pass (a few Harbor-only tests skip on Python < 3.12)
```

For plays 3 and 4 you also need Docker (running) and
[uv](https://docs.astral.sh/uv/) (Harbor needs Python 3.12; the Makefile runs
it through `uvx`, so nothing else to install).

API keys, as environment variables:

- `GEMINI_API_KEY` for play 1 (a free-tier key from Google AI Studio is enough);
- `ANTHROPIC_API_KEY` (or `HANDOFF_ANTHROPIC_API_KEY`, if your agent reserves
  the first name) for play 2, and for play 4 if you use Claude Code.

**Keys and saved episodes.** Plays 1 and 2 run the agent's shell commands on
your machine (mini-swe-agent's LocalEnvironment, not a container). The runner
blanks every secret-looking variable (`*KEY*`, `*TOKEN*`, `*SECRET*`, ...) in
that shell and scrubs saved episodes of your key values and anything shaped like
a known credential (`tools/secrets_guard.py`). Still, an episode can hold other
host details if an agent lists its environment, so before committing episodes
run `git diff --cached | grep -iE 'key|token|secret|proxy'` and read what it
finds. GitHub push protection is the last line, not the first. Use a key with a
spend limit, and rotate it if it ever appears in a file.

---

## 1. Finish the free-tier Gemma pilot

**What it is.** Milestone 1's 30 tasks run by two Gemma models, with a Gemini
model as the frozen consumer. It is a pilot, not a Milestone 1 result (a
different consumer is a different benchmark, DESIGN.md §4), but it exercises
every stage on real models: episodes, consumer judgments, noise floor,
comparison.

**Run it.** Copy the saved episodes to where the runner resumes from, then
start it:

```bash
mkdir -p build/milestone1-pilot-gemini_gemini-3.1-flash-lite
cp -r results/milestone1-pilot-gemma/episodes build/milestone1-pilot-gemini_gemini-3.1-flash-lite/
make pilot-gemini GEMINI_MODELS=gemini/gemma-4-31b-it,gemini/gemma-4-26b-a4b-it \
                  GEMINI_CONSUMER=gemini/gemini-3.1-flash-lite
```

The first line of output should read `60 episode(s) planned, 14 already on
disk`. Run it where it can keep going for a day (a server, `tmux`, `nohup`).

**What to expect.**

- `You exceeded your current quota ... Please retry in Ns` (HTTP 429): the free
  tier's per-minute token limit. The runner waits and retries; this is normal
  and frequent.
- `InternalServerError` / `ServiceUnavailableError` (HTTP 500/503): Google's
  side. The runner retries these too. If one episode is stuck on them for more
  than an hour, stop the run (Ctrl-C) and start it again: finished episodes are
  kept, only the one in progress is redone.
- Don't switch to the Gemini Flash models to go faster: their free tier allows
  about 20 requests a day, fewer than one episode needs.

**Done when** the run exits after scoring. It writes, under
`build/milestone1-pilot-gemini_gemini-3.1-flash-lite/`:

- `episodes/<model>/<task_id>.json` -- one per episode (60 in total);
- `<model>.md` -- each model's scorecard;
- `comparison.md` -- the two models side by side, with the noise floor.

To re-score without running anything: add `--score-only` (run
`python tools/run_milestone1.py --help` for all options).

**Commit** the episodes and the reports:

```bash
cp -r build/milestone1-pilot-gemini_gemini-3.1-flash-lite/episodes results/milestone1-pilot-gemma/
cp build/milestone1-pilot-gemini_gemini-3.1-flash-lite/*.md results/milestone1-pilot-gemma/
git checkout -b results/gemma-pilot && git add results/milestone1-pilot-gemma
git commit -m "Milestone 1 Gemma pilot: 60/60 episodes and scorecards" && git push -u origin HEAD
```

---

## 2. Milestone 1 for real (Claude)

The run the benchmark's thesis depends on: two models over the same 30 tasks,
judged by the pinned Claude consumer.

```bash
mkdir -p build/milestone1 && cp -r results/milestone1/episodes build/milestone1/   # resume from 18/60
make milestone1                      # both default models; see --help for --models and --max-cost-usd
```

- It stops launching episodes once `--max-cost-usd` (default $20) is reached;
  raise it if you mean to finish all 60.
- Keep the noise floor on (the default). Without it, `comparison.md` cannot
  tell a real gap between models from consumer noise.
- **Done when** `build/milestone1/comparison.md` exists. Commit the episodes
  and reports under `results/milestone1/` as in play 1.

What to look for in `comparison.md`: task correctness close to 100% for both
models (the tasks are meant to be easy), and a decision-yield gap larger than
the measured noise floor. If the gap is inside the noise floor, the thesis
failed at this scale -- that is a result, report it as one.

---

## 3. Check the 39 long-horizon tasks

Before any model runs, confirm the tasks themselves:

```bash
make longhorizon-check          # the committed task dirs match the generators
make longhorizon-harbor-check   # "39 of 39 tasks load in Harbor"
make longhorizon-oracle         # Harbor's oracle agent, in Docker
```

**Expected:** the oracle scores **1.0 on all 39** with 0 exceptions (for
LH31-LH39 the oracle is a solver that reads only the workspace). A `nop` agent
(`uvx --python 3.12 --from 'harbor==0.23.0' harbor run -p longhorizon/tasks -a nop -e docker -n 2 -y`)
scores 0 everywhere except LH9 (0.41), LH17 (0.38) and LH20 (0.51), where
leaving some items alone is correct.

This has not been done with the committed Dockerfiles on a normal network:
the sandbox these tasks were built in could not reach apt or pip during
`docker build`, so its checks used copies without that layer. If a build fails
here, that is the first thing to look at. On Docker Hub rate limits, run
`docker pull python:3.12-slim` once first.

---

## 4. Calibrate the long-horizon track

**The claim to test** (longhorizon/README.md, "Admission gate: the empirical
half"): on each task, one agent without subagents runs out of the 20-minute
timeout, and the same agent with parallel subagents finishes. The minute
figures in each `task.toml` are model estimates; this play measures them.

**Conditions.** One agent harness that can spawn subagents, run twice per task
with the same model:

- **with subagents:** the agent as it ships;
- **without subagents:** the same agent with its subagent tool disabled.

With Harbor's `claude-code` agent (replace `<model>`, e.g. `anthropic/<a Claude model id>`):

```bash
H="uvx --python 3.12 --from harbor==0.23.0 harbor"
TASKS=longhorizon/tasks

# with subagents
$H run -p $TASKS -a claude-code -m <model> -e docker -k 3 -n 2 -y \
   --allow-agent-host api.anthropic.com --job-name lh-with -o jobs

# without subagents (same model; the subagent tool disabled)
$H run -p $TASKS -a claude-code -m <model> -e docker -k 3 -n 2 -y \
   --allow-agent-host api.anthropic.com --ak disallowed_tools=Task,Agent \
   --job-name lh-without -o jobs
```

Why the extra flags:

- `--allow-agent-host`: every task sets `network_mode = "no-network"`, so the
  agent can only reach its model API if you allow that host. Allow nothing else.
- `--ak disallowed_tools=...`: turns off Claude Code's subagent tool. Check one
  trajectory from the "without" job to confirm no subagent was started; if the
  tool has a different name in your Claude Code version, use that name.
- `-k 3`: three trials per task and condition.

**Start small.** Run 3-5 tasks first (`-p longhorizon/tasks/lh25_ticket_triage`
etc., one `-p` per run or a folder holding a few task dirs), check the numbers
make sense, then run all 39.

**Two passes.** First a calibration pass with the timeout raised so both
conditions can finish (`--agent-timeout-multiplier 3`); record each trial's
wall-clock time and tokens. Then the real pass at the task's own timeout (no
multiplier).

**Admission rule**, per task, at the real timeout: keep the task if the
"without subagents" condition passes (reward >= 0.9) in at most 1 of 3 trials
and the "with subagents" condition passes in at least 2 of 3. Record per task:

| task | with: passes / 3 | with: mean minutes | without: passes / 3 | without: mean minutes | admit? |
|---|---|---|---|---|---|

Each trial's reward is in `jobs/<job-name>/<trial>/verifier/reward.txt`, and
the job summary is `jobs/<job-name>/result.json`.

**On a free tier** (e.g. Gemini): don't use wall-clock time. Rate limits make
waiting dominate the clock, and parallel subagents share one per-minute quota,
so the throttling hits hardest exactly the condition that should be faster.
Compare the two conditions at an equal budget of model calls or tokens instead,
and report it as a proxy, not as the timing result.

**What would falsify a task:** the "without subagents" agent passes it --
typically by writing one script that handles every unit. Report those tasks;
they need redesign (more per-unit variation), not a longer timeout.

**Commit** the results table (and the job summaries, not the full
trajectories if they are large) under `results/longhorizon-calibration/`.

---

## Reporting back

Open a pull request with what you ran:

- which plays, which models, which agent and version;
- the numbers: `comparison.md` for plays 1-2, the calibration table for play 4;
- anything that failed, with the error, even if you worked around it.

A negative result (no gap beyond the noise floor, a task a single agent
passes) is as useful as a positive one; report it the same way.
