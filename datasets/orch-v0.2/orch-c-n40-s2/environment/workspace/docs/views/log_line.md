# Log Line view

Module: `views/log_line.py`. Audience: the finance team's weekly review.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0102 | rotate-keys | running | low | `job-0102 | rotate-keys | running vv` |
| job-0676 | compact-logs | failed | normal | `job-0676 | compact-logs | failed --` |
| job-0558 | renew-certs | pending | high | `job-0558 | renew-certs | pending ^^` |
| job-0733 | nightly-backup | pending | low | `job-0733 | nightly-backup | pending vv` |
| job-0556 | rebuild-feed | pending | normal | `job-0556 | rebuild-feed | pending --` |
| job-0357 | rebuild-feed | failed | normal | `job-0357 | rebuild-feed | failed --` |
| job-0657 | nightly-backup | done | high | `job-0657 | nightly-backup | done ^^` |
| job-0181 | reindex-search | pending | normal | `job-0181 | reindex-search | pending --` |
| job-0970 | purge-cache | done | normal | `job-0970 | purge-cache | done --` |
| job-0583 | compact-logs | failed | normal | `job-0583 | compact-logs | failed --` |
| job-0534 | export-ledger | done | high | `job-0534 | export-ledger | done ^^` |
| job-0165 | rebuild-feed | done | normal | `job-0165 | rebuild-feed | done --` |
| job-0676 | resize-images | pending | high | `job-0676 | resize-images | pending ^^` |
| job-0712 | purge-cache | running | high | `job-0712 | purge-cache | running ^^` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
