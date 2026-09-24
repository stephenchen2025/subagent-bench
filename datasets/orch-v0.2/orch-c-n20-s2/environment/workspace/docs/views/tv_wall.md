# Tv Wall view

Module: `views/tv_wall.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0510 | rebuild-feed | done | high | `job-0510 | rebuild-feed | done priority:high` |
| job-0710 | rebuild-feed | running | normal | `job-0710 | rebuild-feed | running priority:normal` |
| job-0914 | purge-cache | running | normal | `job-0914 | purge-cache | running priority:normal` |
| job-0208 | compact-logs | done | low | `job-0208 | compact-logs | done priority:low` |
| job-0122 | rotate-keys | pending | normal | `job-0122 | rotate-keys | pending priority:normal` |
| job-0065 | purge-cache | failed | low | `job-0065 | purge-cache | failed priority:low` |
| job-0234 | sync-inventory | pending | normal | `job-0234 | sync-inventory | pending priority:normal` |
| job-0074 | reindex-search | running | high | `job-0074 | reindex-search | running priority:high` |
| job-0510 | compact-logs | failed | low | `job-0510 | compact-logs | failed priority:low` |
| job-0914 | renew-certs | running | low | `job-0914 | renew-certs | running priority:low` |
| job-0816 | purge-cache | failed | normal | `job-0816 | purge-cache | failed priority:normal` |
| job-0953 | compact-logs | running | high | `job-0953 | compact-logs | running priority:high` |
| job-0124 | invoice-run | done | low | `job-0124 | invoice-run | done priority:low` |
| job-0685 | resize-images | done | high | `job-0685 | resize-images | done priority:high` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
