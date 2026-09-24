# Jira Comment view

Module: `views/jira_comment.py`. Audience: release managers.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0511 | send-digest | done | low | `job-0511 | send-digest | done !` |
| job-0737 | invoice-run | pending | high | `job-0737 | invoice-run | pending !!!` |
| job-0074 | export-ledger | failed | high | `job-0074 | export-ledger | failed !!!` |
| job-0867 | export-ledger | running | low | `job-0867 | export-ledger | running !` |
| job-0988 | nightly-backup | done | low | `job-0988 | nightly-backup | done !` |
| job-0861 | sync-inventory | failed | low | `job-0861 | sync-inventory | failed !` |
| job-0927 | export-ledger | done | normal | `job-0927 | export-ledger | done !!` |
| job-0160 | resize-images | done | normal | `job-0160 | resize-images | done !!` |
| job-0784 | export-ledger | pending | normal | `job-0784 | export-ledger | pending !!` |
| job-0991 | reindex-search | running | high | `job-0991 | reindex-search | running !!!` |
| job-0624 | send-digest | failed | low | `job-0624 | send-digest | failed !` |
| job-0749 | rebuild-feed | done | high | `job-0749 | rebuild-feed | done !!!` |
| job-0424 | invoice-run | done | low | `job-0424 | invoice-run | done !` |
| job-0192 | rebuild-feed | done | normal | `job-0192 | rebuild-feed | done !!` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
