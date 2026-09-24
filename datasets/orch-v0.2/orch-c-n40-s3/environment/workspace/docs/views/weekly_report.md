# Weekly Report view

Module: `views/weekly_report.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0614 | invoice-run | failed | low | `invoice-run (job-0614) is failed priority:low` |
| job-0173 | rebuild-feed | running | normal | `rebuild-feed (job-0173) is running priority:normal` |
| job-0837 | rotate-keys | pending | high | `rotate-keys (job-0837) is pending priority:high` |
| job-0245 | resize-images | running | high | `resize-images (job-0245) is running priority:high` |
| job-0225 | rotate-keys | running | high | `rotate-keys (job-0225) is running priority:high` |
| job-0359 | invoice-run | done | high | `invoice-run (job-0359) is done priority:high` |
| job-0773 | export-ledger | done | high | `export-ledger (job-0773) is done priority:high` |
| job-0443 | export-ledger | done | high | `export-ledger (job-0443) is done priority:high` |
| job-0551 | nightly-backup | running | normal | `nightly-backup (job-0551) is running priority:normal` |
| job-0602 | rebuild-feed | running | normal | `rebuild-feed (job-0602) is running priority:normal` |
| job-0412 | rebuild-feed | done | low | `rebuild-feed (job-0412) is done priority:low` |
| job-0517 | renew-certs | pending | high | `renew-certs (job-0517) is pending priority:high` |
| job-0506 | reindex-search | done | high | `reindex-search (job-0506) is done priority:high` |
| job-0396 | nightly-backup | running | low | `nightly-backup (job-0396) is running priority:low` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
