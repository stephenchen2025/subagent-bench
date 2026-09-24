# Markdown List view

Module: `views/markdown_list.py`. Audience: mobile users.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0635 | send-digest | pending | low | `level=1 send-digest (job-0635) is pending` |
| job-0606 | rebuild-feed | done | normal | `level=2 rebuild-feed (job-0606) is done` |
| job-0695 | compact-logs | done | high | `level=3 compact-logs (job-0695) is done` |
| job-0209 | export-ledger | running | low | `level=1 export-ledger (job-0209) is running` |
| job-0926 | purge-cache | pending | high | `level=3 purge-cache (job-0926) is pending` |
| job-0081 | export-ledger | done | low | `level=1 export-ledger (job-0081) is done` |
| job-0198 | rebuild-feed | failed | normal | `level=2 rebuild-feed (job-0198) is failed` |
| job-0276 | export-ledger | running | low | `level=1 export-ledger (job-0276) is running` |
| job-0353 | compact-logs | running | normal | `level=2 compact-logs (job-0353) is running` |
| job-0323 | export-ledger | pending | low | `level=1 export-ledger (job-0323) is pending` |
| job-0873 | nightly-backup | done | low | `level=1 nightly-backup (job-0873) is done` |
| job-0503 | renew-certs | failed | low | `level=1 renew-certs (job-0503) is failed` |
| job-0440 | renew-certs | failed | normal | `level=2 renew-certs (job-0440) is failed` |
| job-0565 | rebuild-feed | done | low | `level=1 rebuild-feed (job-0565) is done` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
