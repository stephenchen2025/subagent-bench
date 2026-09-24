# Milestone 1 -- partial, unscored

Status (2026-09-24): **incomplete. No verdict.**

- Models: `claude-opus-5`, `claude-sonnet-5` (defaults), cost cap in force.
- Episodes completed: 18 of 60, as 9 matched pairs on `f2_ghost_config_0001`–`0009`
  (F2 poisoned premise only). All 18 produced a delimited report.
- Episode spend (mini's accounting, sum of `mini_cost_usd`): $2.04.
- The run stopped when the Anthropic account ran out of credit ("credit balance
  is too low"). Scoring and the noise floor also call the API, so there are no
  per-model reports and no `comparison.md` yet.

To resume, top up the credit, then copy these episodes back and rerun. Completed
episodes are skipped:

    mkdir -p build/milestone1 && cp -r results/milestone1/episodes build/milestone1/
    make milestone1
