# Wiki Table view

Module: `views/wiki_table.py`. Audience: the finance team's weekly review.

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
| job-0957 | invoice-run | running | high | `[HIGH] RUNNING: invoice-run [job-0957]` |
| job-0272 | sync-inventory | failed | normal | `[NORMAL] FAILED: sync-inventory [job-0272]` |
| job-0795 | export-ledger | failed | low | `[LOW] FAILED: export-ledger [job-0795]` |
| job-0833 | invoice-run | running | low | `[LOW] RUNNING: invoice-run [job-0833]` |
| job-0982 | rebuild-feed | failed | low | `[LOW] FAILED: rebuild-feed [job-0982]` |
| job-0690 | send-digest | failed | high | `[HIGH] FAILED: send-digest [job-0690]` |
| job-0019 | invoice-run | pending | high | `[HIGH] PENDING: invoice-run [job-0019]` |
| job-0458 | rotate-keys | failed | low | `[LOW] FAILED: rotate-keys [job-0458]` |
| job-0129 | send-digest | pending | high | `[HIGH] PENDING: send-digest [job-0129]` |
| job-0329 | nightly-backup | pending | high | `[HIGH] PENDING: nightly-backup [job-0329]` |
| job-0439 | invoice-run | pending | high | `[HIGH] PENDING: invoice-run [job-0439]` |
| job-0804 | invoice-run | done | normal | `[NORMAL] DONE: invoice-run [job-0804]` |
| job-0588 | send-digest | done | high | `[HIGH] DONE: send-digest [job-0588]` |
| job-0525 | export-ledger | failed | high | `[HIGH] FAILED: export-ledger [job-0525]` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
