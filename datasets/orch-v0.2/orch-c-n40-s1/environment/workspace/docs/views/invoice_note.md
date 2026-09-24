# Invoice Note view

Module: `views/invoice_note.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0875 | nightly-backup | running | high | `URGENT job job-0875 / nightly-backup / running` |
| job-0893 | sync-inventory | failed | high | `URGENT job job-0893 / sync-inventory / failed` |
| job-0523 | purge-cache | running | low | `DEFERRABLE job job-0523 / purge-cache / running` |
| job-0848 | sync-inventory | done | low | `DEFERRABLE job job-0848 / sync-inventory / done` |
| job-0635 | export-ledger | pending | normal | `ROUTINE job job-0635 / export-ledger / pending` |
| job-0053 | compact-logs | running | low | `DEFERRABLE job job-0053 / compact-logs / running` |
| job-0146 | purge-cache | done | normal | `ROUTINE job job-0146 / purge-cache / done` |
| job-0836 | reindex-search | failed | high | `URGENT job job-0836 / reindex-search / failed` |
| job-0212 | compact-logs | failed | high | `URGENT job job-0212 / compact-logs / failed` |
| job-0321 | send-digest | done | low | `DEFERRABLE job job-0321 / send-digest / done` |
| job-0465 | purge-cache | running | low | `DEFERRABLE job job-0465 / purge-cache / running` |
| job-0216 | invoice-run | running | normal | `ROUTINE job job-0216 / invoice-run / running` |
| job-0108 | send-digest | failed | high | `URGENT job job-0108 / send-digest / failed` |
| job-0867 | reindex-search | done | normal | `ROUTINE job job-0867 / reindex-search / done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
