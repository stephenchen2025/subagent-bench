# Exec Summary view

Module: `views/exec_summary.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0468 | export-ledger | running | low | `color=green RUNNING: export-ledger [job-0468]` |
| job-0623 | reindex-search | running | normal | `color=amber RUNNING: reindex-search [job-0623]` |
| job-0209 | purge-cache | done | high | `color=red DONE: purge-cache [job-0209]` |
| job-0747 | compact-logs | pending | high | `color=red PENDING: compact-logs [job-0747]` |
| job-0731 | rebuild-feed | failed | low | `color=green FAILED: rebuild-feed [job-0731]` |
| job-0892 | send-digest | failed | low | `color=green FAILED: send-digest [job-0892]` |
| job-0773 | reindex-search | failed | normal | `color=amber FAILED: reindex-search [job-0773]` |
| job-0524 | sync-inventory | running | normal | `color=amber RUNNING: sync-inventory [job-0524]` |
| job-0006 | purge-cache | pending | low | `color=green PENDING: purge-cache [job-0006]` |
| job-0085 | rebuild-feed | failed | high | `color=red FAILED: rebuild-feed [job-0085]` |
| job-0815 | invoice-run | pending | high | `color=red PENDING: invoice-run [job-0815]` |
| job-0964 | reindex-search | done | low | `color=green DONE: reindex-search [job-0964]` |
| job-0217 | compact-logs | failed | normal | `color=amber FAILED: compact-logs [job-0217]` |
| job-0420 | sync-inventory | done | normal | `color=amber DONE: sync-inventory [job-0420]` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
