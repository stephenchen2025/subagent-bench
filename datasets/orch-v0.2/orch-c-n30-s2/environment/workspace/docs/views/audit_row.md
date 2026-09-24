# Audit Row view

Module: `views/audit_row.py`. Audience: the on-call engineer who is paged at night.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0359 | reindex-search | done | low | `! job job-0359 / reindex-search / done` |
| job-0081 | sync-inventory | failed | high | `!!! job job-0081 / sync-inventory / failed` |
| job-0412 | reindex-search | pending | high | `!!! job job-0412 / reindex-search / pending` |
| job-0627 | nightly-backup | pending | high | `!!! job job-0627 / nightly-backup / pending` |
| job-0894 | reindex-search | pending | normal | `!! job job-0894 / reindex-search / pending` |
| job-0116 | nightly-backup | running | low | `! job job-0116 / nightly-backup / running` |
| job-0687 | resize-images | pending | normal | `!! job job-0687 / resize-images / pending` |
| job-0771 | export-ledger | failed | low | `! job job-0771 / export-ledger / failed` |
| job-0310 | rotate-keys | running | normal | `!! job job-0310 / rotate-keys / running` |
| job-0804 | export-ledger | pending | normal | `!! job job-0804 / export-ledger / pending` |
| job-0856 | compact-logs | failed | normal | `!! job job-0856 / compact-logs / failed` |
| job-0376 | rotate-keys | pending | high | `!!! job job-0376 / rotate-keys / pending` |
| job-0778 | invoice-run | pending | low | `! job job-0778 / invoice-run / pending` |
| job-0812 | export-ledger | failed | low | `! job job-0812 / export-ledger / failed` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
