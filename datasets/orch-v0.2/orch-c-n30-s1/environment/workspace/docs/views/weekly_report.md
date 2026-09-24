# Weekly Report view

Module: `views/weekly_report.py`. Audience: the platform team's wall display.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0924 | sync-inventory | pending | low | `job-0924 | sync-inventory | pending !` |
| job-0212 | rotate-keys | running | high | `job-0212 | rotate-keys | running !!!` |
| job-0298 | nightly-backup | pending | high | `job-0298 | nightly-backup | pending !!!` |
| job-0325 | invoice-run | failed | high | `job-0325 | invoice-run | failed !!!` |
| job-0779 | nightly-backup | done | normal | `job-0779 | nightly-backup | done !!` |
| job-0400 | invoice-run | pending | high | `job-0400 | invoice-run | pending !!!` |
| job-0625 | resize-images | running | high | `job-0625 | resize-images | running !!!` |
| job-0794 | nightly-backup | pending | low | `job-0794 | nightly-backup | pending !` |
| job-0650 | reindex-search | running | high | `job-0650 | reindex-search | running !!!` |
| job-0659 | purge-cache | pending | normal | `job-0659 | purge-cache | pending !!` |
| job-0785 | purge-cache | pending | high | `job-0785 | purge-cache | pending !!!` |
| job-0807 | send-digest | running | high | `job-0807 | send-digest | running !!!` |
| job-0743 | purge-cache | failed | high | `job-0743 | purge-cache | failed !!!` |
| job-0806 | sync-inventory | done | normal | `job-0806 | sync-inventory | done !!` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
