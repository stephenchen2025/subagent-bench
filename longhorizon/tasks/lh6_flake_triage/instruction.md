# Triage the quarantined flaky tests

`QUARANTINE.md` lists the tests we quarantined this quarter. Before anyone
starts fixing them we need the root-cause category of each. The tests are in
`tests/flaky/`, the code under test is in `src/app/`, and excerpts of six recent
CI runs of each test are in `ci/<test>/` (see `ci/README.md`).

Choose one cause per test from: `order_dependence`, `timing`,
`unseeded_random`, `timezone`, `network`, `resource_leak`, or `insufficient`
(the evidence available does not establish the cause).

Write `/workspace/triage/triage.json`:

```json
{"<test id>": {"cause": "timing", "evidence": "<what in the source and the runs shows it>"}}
```

A test left out counts as wrong. Do not modify tests or source.
