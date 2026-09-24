# Wiki Table view

Module: `views/wiki_table.py`. Audience: the finance team's weekly review.

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
| job-0333 | invoice-run | pending | high | `[HIGH] invoice-run (job-0333) is pending` |
| job-0882 | rebuild-feed | done | normal | `[NORMAL] rebuild-feed (job-0882) is done` |
| job-0677 | rotate-keys | failed | normal | `[NORMAL] rotate-keys (job-0677) is failed` |
| job-0128 | rotate-keys | pending | high | `[HIGH] rotate-keys (job-0128) is pending` |
| job-0633 | rebuild-feed | done | normal | `[NORMAL] rebuild-feed (job-0633) is done` |
| job-0878 | resize-images | done | low | `[LOW] resize-images (job-0878) is done` |
| job-0529 | resize-images | done | high | `[HIGH] resize-images (job-0529) is done` |
| job-0412 | export-ledger | failed | low | `[LOW] export-ledger (job-0412) is failed` |
| job-0002 | rotate-keys | running | normal | `[NORMAL] rotate-keys (job-0002) is running` |
| job-0460 | invoice-run | pending | normal | `[NORMAL] invoice-run (job-0460) is pending` |
| job-0551 | purge-cache | failed | high | `[HIGH] purge-cache (job-0551) is failed` |
| job-0815 | purge-cache | pending | low | `[LOW] purge-cache (job-0815) is pending` |
| job-0013 | reindex-search | failed | high | `[HIGH] reindex-search (job-0013) is failed` |
| job-0568 | sync-inventory | done | low | `[LOW] sync-inventory (job-0568) is done` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
