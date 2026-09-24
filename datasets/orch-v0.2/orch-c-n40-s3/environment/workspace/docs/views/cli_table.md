# Cli Table view

Module: `views/cli_table.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0436 | rebuild-feed | running | high | `rebuild-feed (job-0436) is running [HIGH]` |
| job-0066 | reindex-search | pending | low | `reindex-search (job-0066) is pending [LOW]` |
| job-0407 | nightly-backup | pending | high | `nightly-backup (job-0407) is pending [HIGH]` |
| job-0764 | compact-logs | pending | high | `compact-logs (job-0764) is pending [HIGH]` |
| job-0004 | rebuild-feed | running | low | `rebuild-feed (job-0004) is running [LOW]` |
| job-0088 | renew-certs | done | low | `renew-certs (job-0088) is done [LOW]` |
| job-0223 | rebuild-feed | failed | high | `rebuild-feed (job-0223) is failed [HIGH]` |
| job-0209 | reindex-search | pending | low | `reindex-search (job-0209) is pending [LOW]` |
| job-0830 | nightly-backup | failed | high | `nightly-backup (job-0830) is failed [HIGH]` |
| job-0390 | invoice-run | pending | normal | `invoice-run (job-0390) is pending [NORMAL]` |
| job-0021 | invoice-run | pending | high | `invoice-run (job-0021) is pending [HIGH]` |
| job-0715 | invoice-run | failed | normal | `invoice-run (job-0715) is failed [NORMAL]` |
| job-0137 | compact-logs | failed | high | `compact-logs (job-0137) is failed [HIGH]` |
| job-0944 | purge-cache | done | low | `purge-cache (job-0944) is done [LOW]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
