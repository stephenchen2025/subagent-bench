# Rss Item view

Module: `views/rss_item.py`. Audience: release managers.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0609 | export-ledger | done | low | `job-0609 | export-ledger | done P3` |
| job-0827 | rotate-keys | failed | normal | `job-0827 | rotate-keys | failed P2` |
| job-0152 | sync-inventory | failed | low | `job-0152 | sync-inventory | failed P3` |
| job-0477 | reindex-search | running | low | `job-0477 | reindex-search | running P3` |
| job-0924 | sync-inventory | done | high | `job-0924 | sync-inventory | done P1` |
| job-0025 | export-ledger | done | low | `job-0025 | export-ledger | done P3` |
| job-0602 | resize-images | done | normal | `job-0602 | resize-images | done P2` |
| job-0171 | export-ledger | running | normal | `job-0171 | export-ledger | running P2` |
| job-0022 | purge-cache | done | normal | `job-0022 | purge-cache | done P2` |
| job-0737 | compact-logs | failed | high | `job-0737 | compact-logs | failed P1` |
| job-0937 | rotate-keys | running | high | `job-0937 | rotate-keys | running P1` |
| job-0240 | rebuild-feed | failed | high | `job-0240 | rebuild-feed | failed P1` |
| job-0490 | sync-inventory | done | low | `job-0490 | sync-inventory | done P3` |
| job-0458 | reindex-search | running | high | `job-0458 | reindex-search | running P1` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
