# Json Feed view

Module: `views/json_feed.py`. Audience: the finance team's weekly review.

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
| job-0673 | compact-logs | failed | normal | `job-0673 | compact-logs | failed priority:normal` |
| job-0783 | rotate-keys | pending | low | `job-0783 | rotate-keys | pending priority:low` |
| job-0892 | renew-certs | pending | normal | `job-0892 | renew-certs | pending priority:normal` |
| job-0649 | invoice-run | failed | normal | `job-0649 | invoice-run | failed priority:normal` |
| job-0319 | purge-cache | done | high | `job-0319 | purge-cache | done priority:high` |
| job-0886 | rebuild-feed | pending | normal | `job-0886 | rebuild-feed | pending priority:normal` |
| job-0660 | nightly-backup | pending | high | `job-0660 | nightly-backup | pending priority:high` |
| job-0874 | send-digest | failed | high | `job-0874 | send-digest | failed priority:high` |
| job-0285 | rotate-keys | running | normal | `job-0285 | rotate-keys | running priority:normal` |
| job-0307 | rotate-keys | pending | low | `job-0307 | rotate-keys | pending priority:low` |
| job-0368 | nightly-backup | failed | high | `job-0368 | nightly-backup | failed priority:high` |
| job-0111 | reindex-search | pending | low | `job-0111 | reindex-search | pending priority:low` |
| job-0907 | export-ledger | running | high | `job-0907 | export-ledger | running priority:high` |
| job-0802 | sync-inventory | done | low | `job-0802 | sync-inventory | done priority:low` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
