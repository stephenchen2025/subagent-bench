# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: the finance team's weekly review.

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
| job-0245 | invoice-run | done | high | `[HIGH] invoice-run (job-0245) is done` |
| job-0822 | reindex-search | done | normal | `[NORMAL] reindex-search (job-0822) is done` |
| job-0312 | export-ledger | pending | high | `[HIGH] export-ledger (job-0312) is pending` |
| job-0003 | send-digest | failed | high | `[HIGH] send-digest (job-0003) is failed` |
| job-0565 | purge-cache | done | normal | `[NORMAL] purge-cache (job-0565) is done` |
| job-0962 | rebuild-feed | failed | low | `[LOW] rebuild-feed (job-0962) is failed` |
| job-0378 | rebuild-feed | running | high | `[HIGH] rebuild-feed (job-0378) is running` |
| job-0856 | nightly-backup | running | high | `[HIGH] nightly-backup (job-0856) is running` |
| job-0508 | sync-inventory | done | high | `[HIGH] sync-inventory (job-0508) is done` |
| job-0730 | renew-certs | done | low | `[LOW] renew-certs (job-0730) is done` |
| job-0012 | rebuild-feed | pending | high | `[HIGH] rebuild-feed (job-0012) is pending` |
| job-0207 | sync-inventory | done | normal | `[NORMAL] sync-inventory (job-0207) is done` |
| job-0623 | rebuild-feed | running | high | `[HIGH] rebuild-feed (job-0623) is running` |
| job-0799 | purge-cache | done | normal | `[NORMAL] purge-cache (job-0799) is done` |

## History

- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
