# Json Feed view

Module: `views/json_feed.py`. Audience: the finance team's weekly review.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0503 | send-digest | done | high | `!!! DONE: send-digest [job-0503]` |
| job-0377 | purge-cache | running | high | `!!! RUNNING: purge-cache [job-0377]` |
| job-0289 | reindex-search | done | normal | `!! DONE: reindex-search [job-0289]` |
| job-0386 | purge-cache | running | low | `! RUNNING: purge-cache [job-0386]` |
| job-0560 | rebuild-feed | running | high | `!!! RUNNING: rebuild-feed [job-0560]` |
| job-0368 | compact-logs | failed | low | `! FAILED: compact-logs [job-0368]` |
| job-0100 | sync-inventory | failed | high | `!!! FAILED: sync-inventory [job-0100]` |
| job-0679 | sync-inventory | pending | high | `!!! PENDING: sync-inventory [job-0679]` |
| job-0227 | export-ledger | running | low | `! RUNNING: export-ledger [job-0227]` |
| job-0282 | export-ledger | running | low | `! RUNNING: export-ledger [job-0282]` |
| job-0264 | compact-logs | pending | normal | `!! PENDING: compact-logs [job-0264]` |
| job-0403 | resize-images | done | low | `! DONE: resize-images [job-0403]` |
| job-0446 | nightly-backup | failed | low | `! FAILED: nightly-backup [job-0446]` |
| job-0286 | reindex-search | pending | high | `!!! PENDING: reindex-search [job-0286]` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
