# Results

Everything here was produced **without a real model**; no API key has been
available yet. These results establish that the tasks are valid and that the
metrics separate delegation policies as designed. They say nothing about how
any real model delegates.

| Path | What | How it was produced |
|---|---|---|
| [`harbor-oracle.md`](harbor-oracle.md) | 36/36 tasks score 1.0 with their oracle solutions | `harbor run -p datasets/orch-v0.2 -a oracle` in Docker, summarised by `tools/orch_oracle_summary.py` |
| [`rehearsal-local/`](rehearsal-local/report.md) | 6 scripted policies × 36 tasks = 216 runs | `tools/orch_rehearse.py` (mini-swe-agent's LocalEnvironment) |
| [`rehearsal-harbor/`](rehearsal-harbor/report.md) | the same 216 runs in Docker under Harbor | `harbor run -a orch.harbor_agent:OrchRehearsalAgent --ak system=<policy>`, then `tools/orch_collect.py` |

The two rehearsals agree on every one of the 72 (condition, family, size) cells,
so running through Harbor and Docker changes nothing about the scores. (Three
Docker trials were re-run: their image builds failed because the dataset was
being regenerated while the job read it. The rerun is part of the record.)

Each directory's `records.json` holds one record per run: reward, telemetry
(per-agent steps, peak context, tokens, briefs, worker reports), final answer
and ground truth. `report.md` and the SVGs are rendered from it
(`orch/report.py`), so re-scoring after a metrics change needs no re-runs.

**Next:** `results/<model>/` from a real run. With `ANTHROPIC_API_KEY` set:
`make orch-run MODELS=anthropic/claude-haiku-4-5-20251001`, or the Harbor commands in the
top-level README.
