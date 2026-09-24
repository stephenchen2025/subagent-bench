# Calendar Note view

Module: `views/calendar_note.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0375 | invoice-run | done | low | `! invoice-run (job-0375) is done` |
| job-0143 | nightly-backup | failed | low | `! nightly-backup (job-0143) is failed` |
| job-0298 | invoice-run | running | high | `!!! invoice-run (job-0298) is running` |
| job-0861 | reindex-search | running | normal | `!! reindex-search (job-0861) is running` |
| job-0973 | renew-certs | running | low | `! renew-certs (job-0973) is running` |
| job-0942 | reindex-search | running | high | `!!! reindex-search (job-0942) is running` |
| job-0889 | purge-cache | pending | low | `! purge-cache (job-0889) is pending` |
| job-0581 | sync-inventory | pending | normal | `!! sync-inventory (job-0581) is pending` |
| job-0454 | send-digest | running | high | `!!! send-digest (job-0454) is running` |
| job-0669 | resize-images | failed | normal | `!! resize-images (job-0669) is failed` |
| job-0392 | invoice-run | pending | low | `! invoice-run (job-0392) is pending` |
| job-0002 | invoice-run | running | high | `!!! invoice-run (job-0002) is running` |
| job-0574 | invoice-run | pending | high | `!!! invoice-run (job-0574) is pending` |
| job-0849 | export-ledger | pending | low | `! export-ledger (job-0849) is pending` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
