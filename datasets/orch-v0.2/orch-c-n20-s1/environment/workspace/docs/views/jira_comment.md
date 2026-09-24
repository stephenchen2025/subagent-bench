# Jira Comment view

Module: `views/jira_comment.py`. Audience: the executive summary email.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0708 | rebuild-feed | running | low | `rebuild-feed (job-0708) is running !` |
| job-0423 | purge-cache | pending | low | `purge-cache (job-0423) is pending !` |
| job-0978 | rebuild-feed | failed | normal | `rebuild-feed (job-0978) is failed !!` |
| job-0994 | nightly-backup | running | high | `nightly-backup (job-0994) is running !!!` |
| job-0670 | send-digest | running | low | `send-digest (job-0670) is running !` |
| job-0013 | nightly-backup | running | normal | `nightly-backup (job-0013) is running !!` |
| job-0121 | resize-images | pending | normal | `resize-images (job-0121) is pending !!` |
| job-0847 | reindex-search | done | normal | `reindex-search (job-0847) is done !!` |
| job-0541 | nightly-backup | running | normal | `nightly-backup (job-0541) is running !!` |
| job-0512 | export-ledger | done | normal | `export-ledger (job-0512) is done !!` |
| job-0887 | send-digest | done | low | `send-digest (job-0887) is done !` |
| job-0578 | reindex-search | pending | low | `reindex-search (job-0578) is pending !` |
| job-0057 | sync-inventory | pending | low | `sync-inventory (job-0057) is pending !` |
| job-0802 | purge-cache | done | low | `purge-cache (job-0802) is done !` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
