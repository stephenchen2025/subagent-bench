# Which columns can we drop?

The DBA team wants to delete the columns in `proposals/drop_columns.md` to
reclaim space before the storage migration. `docs/DROP_POLICY.md` defines what
counts as a production use.

For every proposed column, decide:

- `safe`: nothing in production reads or writes it;
- `unsafe`: something does. Give one production location as `<path>:<line>`;
- `insufficient`: this cannot be determined from the repository.

Write `/workspace/answer/columns.json`:

```json
{"<table>.<column>": {"verdict": "unsafe", "location": "app/<path>:<line>"}}
```

A column left out counts as wrong. Do not modify the repository.
