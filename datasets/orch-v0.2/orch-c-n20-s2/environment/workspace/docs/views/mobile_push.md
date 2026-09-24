# Mobile Push view

Module: `views/mobile_push.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0968 | renew-certs | pending | normal | `ROUTINE renew-certs (job-0968) is pending` |
| job-0242 | export-ledger | running | normal | `ROUTINE export-ledger (job-0242) is running` |
| job-0259 | send-digest | done | high | `URGENT send-digest (job-0259) is done` |
| job-0856 | rotate-keys | pending | high | `URGENT rotate-keys (job-0856) is pending` |
| job-0740 | purge-cache | done | low | `DEFERRABLE purge-cache (job-0740) is done` |
| job-0675 | resize-images | failed | low | `DEFERRABLE resize-images (job-0675) is failed` |
| job-0289 | purge-cache | running | normal | `ROUTINE purge-cache (job-0289) is running` |
| job-0500 | purge-cache | failed | high | `URGENT purge-cache (job-0500) is failed` |
| job-0215 | compact-logs | done | high | `URGENT compact-logs (job-0215) is done` |
| job-0245 | nightly-backup | done | low | `DEFERRABLE nightly-backup (job-0245) is done` |
| job-0989 | renew-certs | done | low | `DEFERRABLE renew-certs (job-0989) is done` |
| job-0979 | reindex-search | failed | high | `URGENT reindex-search (job-0979) is failed` |
| job-0607 | reindex-search | failed | high | `URGENT reindex-search (job-0607) is failed` |
| job-0977 | send-digest | pending | high | `URGENT send-digest (job-0977) is pending` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
