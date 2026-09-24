# Sheet Row view

Module: `views/sheet_row.py`. Audience: the on-call engineer who is paged at night.

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
| job-0521 | renew-certs | failed | high | `FAILED: renew-certs [job-0521] URGENT` |
| job-0908 | reindex-search | done | normal | `DONE: reindex-search [job-0908] ROUTINE` |
| job-0966 | resize-images | pending | high | `PENDING: resize-images [job-0966] URGENT` |
| job-0334 | rebuild-feed | failed | low | `FAILED: rebuild-feed [job-0334] DEFERRABLE` |
| job-0844 | purge-cache | pending | low | `PENDING: purge-cache [job-0844] DEFERRABLE` |
| job-0877 | sync-inventory | running | normal | `RUNNING: sync-inventory [job-0877] ROUTINE` |
| job-0142 | renew-certs | running | normal | `RUNNING: renew-certs [job-0142] ROUTINE` |
| job-0726 | resize-images | failed | low | `FAILED: resize-images [job-0726] DEFERRABLE` |
| job-0703 | invoice-run | done | normal | `DONE: invoice-run [job-0703] ROUTINE` |
| job-0924 | compact-logs | failed | normal | `FAILED: compact-logs [job-0924] ROUTINE` |
| job-0957 | renew-certs | pending | high | `PENDING: renew-certs [job-0957] URGENT` |
| job-0476 | reindex-search | failed | high | `FAILED: reindex-search [job-0476] URGENT` |
| job-0632 | rebuild-feed | running | high | `RUNNING: rebuild-feed [job-0632] URGENT` |
| job-0520 | sync-inventory | running | normal | `RUNNING: sync-inventory [job-0520] ROUTINE` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
