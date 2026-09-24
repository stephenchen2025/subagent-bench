# Pager Line view

Module: `views/pager_line.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0832 | compact-logs | failed | low | `[LOW] compact-logs (job-0832) is failed` |
| job-0076 | rebuild-feed | done | high | `[HIGH] rebuild-feed (job-0076) is done` |
| job-0305 | resize-images | running | high | `[HIGH] resize-images (job-0305) is running` |
| job-0623 | renew-certs | running | low | `[LOW] renew-certs (job-0623) is running` |
| job-0886 | sync-inventory | running | low | `[LOW] sync-inventory (job-0886) is running` |
| job-0620 | send-digest | running | low | `[LOW] send-digest (job-0620) is running` |
| job-0876 | sync-inventory | done | low | `[LOW] sync-inventory (job-0876) is done` |
| job-0696 | rebuild-feed | running | normal | `[NORMAL] rebuild-feed (job-0696) is running` |
| job-0251 | reindex-search | done | high | `[HIGH] reindex-search (job-0251) is done` |
| job-0610 | reindex-search | pending | normal | `[NORMAL] reindex-search (job-0610) is pending` |
| job-0276 | rebuild-feed | running | high | `[HIGH] rebuild-feed (job-0276) is running` |
| job-0348 | resize-images | running | high | `[HIGH] resize-images (job-0348) is running` |
| job-0823 | purge-cache | failed | low | `[LOW] purge-cache (job-0823) is failed` |
| job-0550 | renew-certs | running | normal | `[NORMAL] renew-certs (job-0550) is running` |

## History

- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
