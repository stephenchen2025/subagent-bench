# Log Line view

Module: `views/log_line.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0450 | nightly-backup | running | high | `URGENT RUNNING: nightly-backup [job-0450]` |
| job-0192 | invoice-run | failed | low | `DEFERRABLE FAILED: invoice-run [job-0192]` |
| job-0958 | sync-inventory | pending | high | `URGENT PENDING: sync-inventory [job-0958]` |
| job-0937 | resize-images | failed | high | `URGENT FAILED: resize-images [job-0937]` |
| job-0315 | purge-cache | pending | normal | `ROUTINE PENDING: purge-cache [job-0315]` |
| job-0416 | rotate-keys | running | low | `DEFERRABLE RUNNING: rotate-keys [job-0416]` |
| job-0117 | sync-inventory | done | low | `DEFERRABLE DONE: sync-inventory [job-0117]` |
| job-0937 | invoice-run | running | normal | `ROUTINE RUNNING: invoice-run [job-0937]` |
| job-0768 | sync-inventory | running | low | `DEFERRABLE RUNNING: sync-inventory [job-0768]` |
| job-0819 | nightly-backup | running | high | `URGENT RUNNING: nightly-backup [job-0819]` |
| job-0144 | rebuild-feed | running | normal | `ROUTINE RUNNING: rebuild-feed [job-0144]` |
| job-0133 | compact-logs | failed | normal | `ROUTINE FAILED: compact-logs [job-0133]` |
| job-0018 | invoice-run | running | low | `DEFERRABLE RUNNING: invoice-run [job-0018]` |
| job-0360 | export-ledger | done | normal | `ROUTINE DONE: export-ledger [job-0360]` |

## History

- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
