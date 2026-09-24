# Wiki Table view

Module: `views/wiki_table.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0696 | purge-cache | done | normal | `purge-cache (job-0696) is done priority:normal` |
| job-0589 | sync-inventory | pending | normal | `sync-inventory (job-0589) is pending priority:normal` |
| job-0623 | rebuild-feed | done | low | `rebuild-feed (job-0623) is done priority:low` |
| job-0012 | compact-logs | done | normal | `compact-logs (job-0012) is done priority:normal` |
| job-0619 | nightly-backup | pending | high | `nightly-backup (job-0619) is pending priority:high` |
| job-0959 | sync-inventory | running | low | `sync-inventory (job-0959) is running priority:low` |
| job-0735 | nightly-backup | failed | normal | `nightly-backup (job-0735) is failed priority:normal` |
| job-0268 | export-ledger | pending | low | `export-ledger (job-0268) is pending priority:low` |
| job-0830 | sync-inventory | failed | high | `sync-inventory (job-0830) is failed priority:high` |
| job-0664 | purge-cache | done | normal | `purge-cache (job-0664) is done priority:normal` |
| job-0312 | purge-cache | done | low | `purge-cache (job-0312) is done priority:low` |
| job-0126 | nightly-backup | done | normal | `nightly-backup (job-0126) is done priority:normal` |
| job-0386 | export-ledger | done | high | `export-ledger (job-0386) is done priority:high` |
| job-0731 | send-digest | running | low | `send-digest (job-0731) is running priority:low` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
