# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0342 | sync-inventory | done | normal | `job job-0342 / sync-inventory / done **` |
| job-0418 | nightly-backup | failed | high | `job job-0418 / nightly-backup / failed ***` |
| job-0343 | compact-logs | running | normal | `job job-0343 / compact-logs / running **` |
| job-0663 | renew-certs | failed | normal | `job job-0663 / renew-certs / failed **` |
| job-0367 | compact-logs | pending | high | `job job-0367 / compact-logs / pending ***` |
| job-0796 | rebuild-feed | pending | low | `job job-0796 / rebuild-feed / pending *` |
| job-0715 | invoice-run | running | low | `job job-0715 / invoice-run / running *` |
| job-0510 | sync-inventory | done | low | `job job-0510 / sync-inventory / done *` |
| job-0274 | purge-cache | pending | normal | `job job-0274 / purge-cache / pending **` |
| job-0083 | nightly-backup | pending | low | `job job-0083 / nightly-backup / pending *` |
| job-0760 | resize-images | running | normal | `job job-0760 / resize-images / running **` |
| job-0754 | reindex-search | running | low | `job job-0754 / reindex-search / running *` |
| job-0134 | sync-inventory | done | normal | `job job-0134 / sync-inventory / done **` |
| job-0526 | resize-images | failed | low | `job job-0526 / resize-images / failed *` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
