# Exec Summary view

Module: `views/exec_summary.py`. Audience: the executive summary email.

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
| job-0442 | renew-certs | done | normal | `job-0442 | renew-certs | done **` |
| job-0782 | rotate-keys | done | low | `job-0782 | rotate-keys | done *` |
| job-0842 | resize-images | running | high | `job-0842 | resize-images | running ***` |
| job-0368 | purge-cache | failed | high | `job-0368 | purge-cache | failed ***` |
| job-0252 | rebuild-feed | done | normal | `job-0252 | rebuild-feed | done **` |
| job-0423 | renew-certs | pending | normal | `job-0423 | renew-certs | pending **` |
| job-0530 | nightly-backup | running | normal | `job-0530 | nightly-backup | running **` |
| job-0628 | invoice-run | done | low | `job-0628 | invoice-run | done *` |
| job-0256 | resize-images | running | low | `job-0256 | resize-images | running *` |
| job-0086 | rebuild-feed | done | high | `job-0086 | rebuild-feed | done ***` |
| job-0886 | rebuild-feed | done | low | `job-0886 | rebuild-feed | done *` |
| job-0858 | reindex-search | failed | high | `job-0858 | reindex-search | failed ***` |
| job-0456 | rebuild-feed | running | normal | `job-0456 | rebuild-feed | running **` |
| job-0241 | compact-logs | done | normal | `job-0241 | compact-logs | done **` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
