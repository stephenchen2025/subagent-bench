# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: release managers.

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
| job-0315 | resize-images | done | high | `resize-images (job-0315) is done priority:high` |
| job-0801 | nightly-backup | pending | normal | `nightly-backup (job-0801) is pending priority:normal` |
| job-0327 | nightly-backup | failed | low | `nightly-backup (job-0327) is failed priority:low` |
| job-0736 | resize-images | done | normal | `resize-images (job-0736) is done priority:normal` |
| job-0259 | compact-logs | failed | high | `compact-logs (job-0259) is failed priority:high` |
| job-0730 | rebuild-feed | failed | high | `rebuild-feed (job-0730) is failed priority:high` |
| job-0306 | purge-cache | pending | low | `purge-cache (job-0306) is pending priority:low` |
| job-0053 | purge-cache | pending | low | `purge-cache (job-0053) is pending priority:low` |
| job-0799 | sync-inventory | pending | low | `sync-inventory (job-0799) is pending priority:low` |
| job-0497 | nightly-backup | running | high | `nightly-backup (job-0497) is running priority:high` |
| job-0051 | send-digest | failed | low | `send-digest (job-0051) is failed priority:low` |
| job-0937 | compact-logs | running | normal | `compact-logs (job-0937) is running priority:normal` |
| job-0909 | export-ledger | pending | low | `export-ledger (job-0909) is pending priority:low` |
| job-0359 | rotate-keys | failed | normal | `rotate-keys (job-0359) is failed priority:normal` |

## History

- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
