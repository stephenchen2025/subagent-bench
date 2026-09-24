# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: the on-call engineer who is paged at night.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0420 | renew-certs | pending | high | `!!! PENDING: renew-certs [job-0420]` |
| job-0496 | export-ledger | done | low | `! DONE: export-ledger [job-0496]` |
| job-0127 | nightly-backup | done | high | `!!! DONE: nightly-backup [job-0127]` |
| job-0439 | nightly-backup | failed | high | `!!! FAILED: nightly-backup [job-0439]` |
| job-0666 | sync-inventory | running | low | `! RUNNING: sync-inventory [job-0666]` |
| job-0880 | compact-logs | pending | high | `!!! PENDING: compact-logs [job-0880]` |
| job-0747 | resize-images | failed | normal | `!! FAILED: resize-images [job-0747]` |
| job-0125 | rotate-keys | done | high | `!!! DONE: rotate-keys [job-0125]` |
| job-0052 | rebuild-feed | pending | low | `! PENDING: rebuild-feed [job-0052]` |
| job-0623 | compact-logs | done | high | `!!! DONE: compact-logs [job-0623]` |
| job-0151 | sync-inventory | running | high | `!!! RUNNING: sync-inventory [job-0151]` |
| job-0777 | resize-images | failed | high | `!!! FAILED: resize-images [job-0777]` |
| job-0297 | nightly-backup | failed | normal | `!! FAILED: nightly-backup [job-0297]` |
| job-0165 | sync-inventory | pending | normal | `!! PENDING: sync-inventory [job-0165]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
