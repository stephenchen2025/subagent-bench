# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0283 | nightly-backup | done | low | `DONE: nightly-backup [job-0283] level=1` |
| job-0877 | resize-images | failed | low | `FAILED: resize-images [job-0877] level=1` |
| job-0634 | resize-images | pending | low | `PENDING: resize-images [job-0634] level=1` |
| job-0186 | rotate-keys | pending | normal | `PENDING: rotate-keys [job-0186] level=2` |
| job-0924 | resize-images | failed | normal | `FAILED: resize-images [job-0924] level=2` |
| job-0063 | compact-logs | failed | low | `FAILED: compact-logs [job-0063] level=1` |
| job-0111 | compact-logs | failed | high | `FAILED: compact-logs [job-0111] level=3` |
| job-0075 | sync-inventory | done | high | `DONE: sync-inventory [job-0075] level=3` |
| job-0944 | reindex-search | running | normal | `RUNNING: reindex-search [job-0944] level=2` |
| job-0927 | sync-inventory | running | high | `RUNNING: sync-inventory [job-0927] level=3` |
| job-0285 | export-ledger | pending | low | `PENDING: export-ledger [job-0285] level=1` |
| job-0091 | export-ledger | running | normal | `RUNNING: export-ledger [job-0091] level=2` |
| job-0471 | rebuild-feed | running | low | `RUNNING: rebuild-feed [job-0471] level=1` |
| job-0285 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0285] level=1` |

## History

- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
