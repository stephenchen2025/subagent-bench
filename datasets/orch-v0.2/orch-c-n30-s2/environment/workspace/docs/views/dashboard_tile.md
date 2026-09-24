# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: the executive summary email.

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
| job-0759 | purge-cache | done | normal | `job-0759 | purge-cache | done color=amber` |
| job-0290 | reindex-search | running | normal | `job-0290 | reindex-search | running color=amber` |
| job-0256 | purge-cache | pending | normal | `job-0256 | purge-cache | pending color=amber` |
| job-0087 | send-digest | failed | normal | `job-0087 | send-digest | failed color=amber` |
| job-0446 | export-ledger | failed | high | `job-0446 | export-ledger | failed color=red` |
| job-0172 | sync-inventory | pending | normal | `job-0172 | sync-inventory | pending color=amber` |
| job-0180 | rotate-keys | done | normal | `job-0180 | rotate-keys | done color=amber` |
| job-0201 | purge-cache | done | normal | `job-0201 | purge-cache | done color=amber` |
| job-0378 | nightly-backup | failed | low | `job-0378 | nightly-backup | failed color=green` |
| job-0555 | renew-certs | running | high | `job-0555 | renew-certs | running color=red` |
| job-0519 | rebuild-feed | done | low | `job-0519 | rebuild-feed | done color=green` |
| job-0340 | compact-logs | done | high | `job-0340 | compact-logs | done color=red` |
| job-0050 | sync-inventory | failed | high | `job-0050 | sync-inventory | failed color=red` |
| job-0328 | resize-images | running | high | `job-0328 | resize-images | running color=red` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
