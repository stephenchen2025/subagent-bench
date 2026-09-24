# Slack Alert view

Module: `views/slack_alert.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0406 | purge-cache | running | high | `RUNNING: purge-cache [job-0406] URGENT` |
| job-0815 | send-digest | pending | normal | `PENDING: send-digest [job-0815] ROUTINE` |
| job-0870 | sync-inventory | failed | high | `FAILED: sync-inventory [job-0870] URGENT` |
| job-0129 | sync-inventory | running | normal | `RUNNING: sync-inventory [job-0129] ROUTINE` |
| job-0800 | purge-cache | failed | high | `FAILED: purge-cache [job-0800] URGENT` |
| job-0897 | rebuild-feed | failed | normal | `FAILED: rebuild-feed [job-0897] ROUTINE` |
| job-0375 | resize-images | running | normal | `RUNNING: resize-images [job-0375] ROUTINE` |
| job-0780 | send-digest | pending | normal | `PENDING: send-digest [job-0780] ROUTINE` |
| job-0333 | export-ledger | done | normal | `DONE: export-ledger [job-0333] ROUTINE` |
| job-0208 | compact-logs | done | low | `DONE: compact-logs [job-0208] DEFERRABLE` |
| job-0661 | invoice-run | failed | normal | `FAILED: invoice-run [job-0661] ROUTINE` |
| job-0647 | nightly-backup | running | low | `RUNNING: nightly-backup [job-0647] DEFERRABLE` |
| job-0648 | invoice-run | failed | normal | `FAILED: invoice-run [job-0648] ROUTINE` |
| job-0179 | rebuild-feed | pending | low | `PENDING: rebuild-feed [job-0179] DEFERRABLE` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
