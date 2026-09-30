# Clear the billing bug backlog

`issues/` holds the open bug reports against `shop/`. `docs/spec.md` is the
authority on how every function must behave.

Go through every issue. Fix the ones that are real defects. Close the ones that
are not, and link duplicates to the earlier issue for the same defect. Do not
change behaviour the spec requires, even if an issue asks for it.

Record the outcome of every issue in `/workspace/triage.json`:

```json
{"ISSUE-NNN": {"resolution": "fixed" | "duplicate" | "not_a_bug" | "cannot_reproduce",
               "duplicate_of": "ISSUE-NNN (duplicates only)"}}
```
