# Sheet Row view

Module: `views/sheet_row.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0161 | resize-images | done | low | `P3 job job-0161 / resize-images / done` |
| job-0868 | reindex-search | failed | low | `P3 job job-0868 / reindex-search / failed` |
| job-0982 | export-ledger | running | normal | `P2 job job-0982 / export-ledger / running` |
| job-0987 | nightly-backup | done | normal | `P2 job job-0987 / nightly-backup / done` |
| job-0560 | export-ledger | pending | normal | `P2 job job-0560 / export-ledger / pending` |
| job-0939 | sync-inventory | running | high | `P1 job job-0939 / sync-inventory / running` |
| job-0773 | rebuild-feed | failed | low | `P3 job job-0773 / rebuild-feed / failed` |
| job-0928 | sync-inventory | running | normal | `P2 job job-0928 / sync-inventory / running` |
| job-0832 | compact-logs | running | high | `P1 job job-0832 / compact-logs / running` |
| job-0367 | export-ledger | done | normal | `P2 job job-0367 / export-ledger / done` |
| job-0373 | nightly-backup | pending | normal | `P2 job job-0373 / nightly-backup / pending` |
| job-0460 | rotate-keys | done | low | `P3 job job-0460 / rotate-keys / done` |
| job-0244 | rotate-keys | failed | normal | `P2 job job-0244 / rotate-keys / failed` |
| job-0805 | send-digest | running | low | `P3 job job-0805 / send-digest / running` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
