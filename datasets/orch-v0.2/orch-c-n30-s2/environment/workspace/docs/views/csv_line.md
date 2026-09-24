# Csv Line view

Module: `views/csv_line.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0085 | export-ledger | failed | normal | `[NORMAL] FAILED: export-ledger [job-0085]` |
| job-0933 | send-digest | done | low | `[LOW] DONE: send-digest [job-0933]` |
| job-0296 | send-digest | running | high | `[HIGH] RUNNING: send-digest [job-0296]` |
| job-0477 | compact-logs | running | high | `[HIGH] RUNNING: compact-logs [job-0477]` |
| job-0442 | sync-inventory | failed | normal | `[NORMAL] FAILED: sync-inventory [job-0442]` |
| job-0540 | send-digest | running | normal | `[NORMAL] RUNNING: send-digest [job-0540]` |
| job-0526 | rotate-keys | pending | normal | `[NORMAL] PENDING: rotate-keys [job-0526]` |
| job-0225 | invoice-run | running | low | `[LOW] RUNNING: invoice-run [job-0225]` |
| job-0830 | rebuild-feed | done | high | `[HIGH] DONE: rebuild-feed [job-0830]` |
| job-0571 | rebuild-feed | done | high | `[HIGH] DONE: rebuild-feed [job-0571]` |
| job-0266 | send-digest | failed | normal | `[NORMAL] FAILED: send-digest [job-0266]` |
| job-0582 | send-digest | running | high | `[HIGH] RUNNING: send-digest [job-0582]` |
| job-0272 | reindex-search | failed | high | `[HIGH] FAILED: reindex-search [job-0272]` |
| job-0099 | resize-images | failed | normal | `[NORMAL] FAILED: resize-images [job-0099]` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
