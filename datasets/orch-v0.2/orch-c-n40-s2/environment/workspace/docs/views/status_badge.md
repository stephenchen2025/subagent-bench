# Status Badge view

Module: `views/status_badge.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0579 | purge-cache | failed | normal | `job-0579 | purge-cache | failed ROUTINE` |
| job-0452 | compact-logs | running | low | `job-0452 | compact-logs | running DEFERRABLE` |
| job-0686 | invoice-run | failed | low | `job-0686 | invoice-run | failed DEFERRABLE` |
| job-0244 | reindex-search | failed | high | `job-0244 | reindex-search | failed URGENT` |
| job-0650 | export-ledger | done | high | `job-0650 | export-ledger | done URGENT` |
| job-0620 | sync-inventory | pending | high | `job-0620 | sync-inventory | pending URGENT` |
| job-0876 | send-digest | done | high | `job-0876 | send-digest | done URGENT` |
| job-0640 | renew-certs | failed | low | `job-0640 | renew-certs | failed DEFERRABLE` |
| job-0913 | rebuild-feed | failed | low | `job-0913 | rebuild-feed | failed DEFERRABLE` |
| job-0097 | nightly-backup | running | low | `job-0097 | nightly-backup | running DEFERRABLE` |
| job-0351 | rebuild-feed | done | low | `job-0351 | rebuild-feed | done DEFERRABLE` |
| job-0651 | nightly-backup | pending | low | `job-0651 | nightly-backup | pending DEFERRABLE` |
| job-0860 | send-digest | failed | normal | `job-0860 | send-digest | failed ROUTINE` |
| job-0675 | invoice-run | done | low | `job-0675 | invoice-run | done DEFERRABLE` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
