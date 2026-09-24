# Weekly Report view

Module: `views/weekly_report.py`. Audience: the on-call engineer who is paged at night.

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
| job-0003 | send-digest | running | low | `RUNNING: send-digest [job-0003] level=1` |
| job-0770 | compact-logs | done | low | `DONE: compact-logs [job-0770] level=1` |
| job-0073 | renew-certs | done | normal | `DONE: renew-certs [job-0073] level=2` |
| job-0165 | resize-images | done | normal | `DONE: resize-images [job-0165] level=2` |
| job-0793 | nightly-backup | running | normal | `RUNNING: nightly-backup [job-0793] level=2` |
| job-0889 | purge-cache | done | low | `DONE: purge-cache [job-0889] level=1` |
| job-0824 | sync-inventory | done | high | `DONE: sync-inventory [job-0824] level=3` |
| job-0478 | resize-images | failed | low | `FAILED: resize-images [job-0478] level=1` |
| job-0731 | export-ledger | done | high | `DONE: export-ledger [job-0731] level=3` |
| job-0844 | nightly-backup | pending | normal | `PENDING: nightly-backup [job-0844] level=2` |
| job-0527 | rebuild-feed | failed | high | `FAILED: rebuild-feed [job-0527] level=3` |
| job-0246 | compact-logs | failed | normal | `FAILED: compact-logs [job-0246] level=2` |
| job-0984 | sync-inventory | done | high | `DONE: sync-inventory [job-0984] level=3` |
| job-0826 | sync-inventory | pending | normal | `PENDING: sync-inventory [job-0826] level=2` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
