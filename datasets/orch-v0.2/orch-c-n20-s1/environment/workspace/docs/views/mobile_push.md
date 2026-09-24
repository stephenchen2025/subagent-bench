# Mobile Push view

Module: `views/mobile_push.py`. Audience: auditors reviewing job history.

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
| job-0693 | compact-logs | pending | low | `job-0693 | compact-logs | pending priority:low` |
| job-0972 | rebuild-feed | failed | normal | `job-0972 | rebuild-feed | failed priority:normal` |
| job-0398 | rebuild-feed | done | normal | `job-0398 | rebuild-feed | done priority:normal` |
| job-0140 | reindex-search | running | low | `job-0140 | reindex-search | running priority:low` |
| job-0274 | compact-logs | running | low | `job-0274 | compact-logs | running priority:low` |
| job-0013 | resize-images | done | normal | `job-0013 | resize-images | done priority:normal` |
| job-0168 | rebuild-feed | pending | normal | `job-0168 | rebuild-feed | pending priority:normal` |
| job-0392 | resize-images | running | low | `job-0392 | resize-images | running priority:low` |
| job-0488 | sync-inventory | done | high | `job-0488 | sync-inventory | done priority:high` |
| job-0703 | renew-certs | pending | high | `job-0703 | renew-certs | pending priority:high` |
| job-0973 | rebuild-feed | done | normal | `job-0973 | rebuild-feed | done priority:normal` |
| job-0436 | purge-cache | done | low | `job-0436 | purge-cache | done priority:low` |
| job-0846 | rebuild-feed | running | normal | `job-0846 | rebuild-feed | running priority:normal` |
| job-0527 | reindex-search | running | normal | `job-0527 | reindex-search | running priority:normal` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
