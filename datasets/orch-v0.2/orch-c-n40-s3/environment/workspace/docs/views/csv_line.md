# Csv Line view

Module: `views/csv_line.py`. Audience: customer support leads.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0560 | rebuild-feed | done | normal | `rebuild-feed (job-0560) is done !!` |
| job-0927 | nightly-backup | failed | high | `nightly-backup (job-0927) is failed !!!` |
| job-0629 | invoice-run | failed | high | `invoice-run (job-0629) is failed !!!` |
| job-0102 | renew-certs | running | normal | `renew-certs (job-0102) is running !!` |
| job-0859 | rebuild-feed | done | normal | `rebuild-feed (job-0859) is done !!` |
| job-0319 | nightly-backup | pending | high | `nightly-backup (job-0319) is pending !!!` |
| job-0599 | renew-certs | done | high | `renew-certs (job-0599) is done !!!` |
| job-0267 | compact-logs | running | high | `compact-logs (job-0267) is running !!!` |
| job-0134 | reindex-search | failed | normal | `reindex-search (job-0134) is failed !!` |
| job-0142 | nightly-backup | pending | high | `nightly-backup (job-0142) is pending !!!` |
| job-0467 | send-digest | done | low | `send-digest (job-0467) is done !` |
| job-0565 | compact-logs | pending | high | `compact-logs (job-0565) is pending !!!` |
| job-0058 | sync-inventory | pending | high | `sync-inventory (job-0058) is pending !!!` |
| job-0052 | export-ledger | running | low | `export-ledger (job-0052) is running !` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
