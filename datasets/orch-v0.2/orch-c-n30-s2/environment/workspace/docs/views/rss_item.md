# Rss Item view

Module: `views/rss_item.py`. Audience: auditors reviewing job history.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0991 | purge-cache | running | normal | `job-0991 | purge-cache | running color=amber` |
| job-0010 | rebuild-feed | failed | high | `job-0010 | rebuild-feed | failed color=red` |
| job-0601 | send-digest | pending | low | `job-0601 | send-digest | pending color=green` |
| job-0938 | purge-cache | failed | normal | `job-0938 | purge-cache | failed color=amber` |
| job-0569 | purge-cache | pending | high | `job-0569 | purge-cache | pending color=red` |
| job-0382 | sync-inventory | failed | low | `job-0382 | sync-inventory | failed color=green` |
| job-0630 | sync-inventory | done | high | `job-0630 | sync-inventory | done color=red` |
| job-0870 | send-digest | done | low | `job-0870 | send-digest | done color=green` |
| job-0948 | send-digest | failed | high | `job-0948 | send-digest | failed color=red` |
| job-0760 | export-ledger | pending | high | `job-0760 | export-ledger | pending color=red` |
| job-0291 | rotate-keys | pending | high | `job-0291 | rotate-keys | pending color=red` |
| job-0161 | reindex-search | done | low | `job-0161 | reindex-search | done color=green` |
| job-0099 | rebuild-feed | pending | low | `job-0099 | rebuild-feed | pending color=green` |
| job-0363 | nightly-backup | running | normal | `job-0363 | nightly-backup | running color=amber` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
