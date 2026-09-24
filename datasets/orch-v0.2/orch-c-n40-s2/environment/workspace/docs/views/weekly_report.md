# Weekly Report view

Module: `views/weekly_report.py`. Audience: the platform team's wall display.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0568 | reindex-search | done | normal | `job-0568 | reindex-search | done **` |
| job-0834 | reindex-search | running | high | `job-0834 | reindex-search | running ***` |
| job-0312 | sync-inventory | done | high | `job-0312 | sync-inventory | done ***` |
| job-0258 | rotate-keys | pending | high | `job-0258 | rotate-keys | pending ***` |
| job-0846 | sync-inventory | pending | low | `job-0846 | sync-inventory | pending *` |
| job-0331 | purge-cache | failed | high | `job-0331 | purge-cache | failed ***` |
| job-0001 | compact-logs | failed | high | `job-0001 | compact-logs | failed ***` |
| job-0159 | reindex-search | failed | normal | `job-0159 | reindex-search | failed **` |
| job-0852 | invoice-run | failed | normal | `job-0852 | invoice-run | failed **` |
| job-0093 | export-ledger | done | low | `job-0093 | export-ledger | done *` |
| job-0092 | invoice-run | running | high | `job-0092 | invoice-run | running ***` |
| job-0458 | export-ledger | done | low | `job-0458 | export-ledger | done *` |
| job-0977 | reindex-search | failed | normal | `job-0977 | reindex-search | failed **` |
| job-0150 | compact-logs | failed | low | `job-0150 | compact-logs | failed *` |

## History

- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
