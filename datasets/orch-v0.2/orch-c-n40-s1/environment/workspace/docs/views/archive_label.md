# Archive Label view

Module: `views/archive_label.py`. Audience: the executive summary email.

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
| job-0816 | invoice-run | pending | normal | `ROUTINE job job-0816 / invoice-run / pending` |
| job-0088 | compact-logs | pending | normal | `ROUTINE job job-0088 / compact-logs / pending` |
| job-0831 | rotate-keys | running | low | `DEFERRABLE job job-0831 / rotate-keys / running` |
| job-0580 | rotate-keys | failed | normal | `ROUTINE job job-0580 / rotate-keys / failed` |
| job-0202 | export-ledger | running | low | `DEFERRABLE job job-0202 / export-ledger / running` |
| job-0722 | nightly-backup | failed | high | `URGENT job job-0722 / nightly-backup / failed` |
| job-0053 | rotate-keys | pending | low | `DEFERRABLE job job-0053 / rotate-keys / pending` |
| job-0310 | nightly-backup | failed | normal | `ROUTINE job job-0310 / nightly-backup / failed` |
| job-0804 | rebuild-feed | done | high | `URGENT job job-0804 / rebuild-feed / done` |
| job-0346 | send-digest | pending | high | `URGENT job job-0346 / send-digest / pending` |
| job-0289 | sync-inventory | pending | low | `DEFERRABLE job job-0289 / sync-inventory / pending` |
| job-0345 | purge-cache | running | low | `DEFERRABLE job job-0345 / purge-cache / running` |
| job-0662 | compact-logs | done | normal | `ROUTINE job job-0662 / compact-logs / done` |
| job-0247 | reindex-search | done | high | `URGENT job job-0247 / reindex-search / done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
