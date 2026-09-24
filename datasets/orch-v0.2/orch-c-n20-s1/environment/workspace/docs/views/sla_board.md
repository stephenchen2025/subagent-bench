# Sla Board view

Module: `views/sla_board.py`. Audience: the finance team's weekly review.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0699 | send-digest | done | low | `job-0699 | send-digest | done [LOW]` |
| job-0638 | send-digest | pending | normal | `job-0638 | send-digest | pending [NORMAL]` |
| job-0485 | rebuild-feed | running | normal | `job-0485 | rebuild-feed | running [NORMAL]` |
| job-0205 | reindex-search | running | low | `job-0205 | reindex-search | running [LOW]` |
| job-0480 | sync-inventory | failed | normal | `job-0480 | sync-inventory | failed [NORMAL]` |
| job-0414 | resize-images | failed | high | `job-0414 | resize-images | failed [HIGH]` |
| job-0772 | rebuild-feed | running | low | `job-0772 | rebuild-feed | running [LOW]` |
| job-0059 | invoice-run | pending | high | `job-0059 | invoice-run | pending [HIGH]` |
| job-0592 | send-digest | done | low | `job-0592 | send-digest | done [LOW]` |
| job-0163 | sync-inventory | done | low | `job-0163 | sync-inventory | done [LOW]` |
| job-0754 | purge-cache | done | high | `job-0754 | purge-cache | done [HIGH]` |
| job-0512 | rebuild-feed | failed | normal | `job-0512 | rebuild-feed | failed [NORMAL]` |
| job-0005 | rebuild-feed | failed | high | `job-0005 | rebuild-feed | failed [HIGH]` |
| job-0554 | send-digest | done | normal | `job-0554 | send-digest | done [NORMAL]` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
