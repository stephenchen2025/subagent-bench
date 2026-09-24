# Archive Label view

Module: `views/archive_label.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0994 | export-ledger | failed | normal | `level=2 export-ledger (job-0994) is failed` |
| job-0530 | compact-logs | done | high | `level=3 compact-logs (job-0530) is done` |
| job-0308 | invoice-run | failed | high | `level=3 invoice-run (job-0308) is failed` |
| job-0990 | nightly-backup | pending | low | `level=1 nightly-backup (job-0990) is pending` |
| job-0961 | resize-images | pending | high | `level=3 resize-images (job-0961) is pending` |
| job-0901 | sync-inventory | pending | high | `level=3 sync-inventory (job-0901) is pending` |
| job-0985 | nightly-backup | failed | high | `level=3 nightly-backup (job-0985) is failed` |
| job-0422 | purge-cache | failed | normal | `level=2 purge-cache (job-0422) is failed` |
| job-0747 | renew-certs | running | low | `level=1 renew-certs (job-0747) is running` |
| job-0487 | send-digest | running | high | `level=3 send-digest (job-0487) is running` |
| job-0803 | send-digest | done | low | `level=1 send-digest (job-0803) is done` |
| job-0756 | compact-logs | done | normal | `level=2 compact-logs (job-0756) is done` |
| job-0939 | resize-images | done | low | `level=1 resize-images (job-0939) is done` |
| job-0122 | reindex-search | running | low | `level=1 reindex-search (job-0122) is running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
