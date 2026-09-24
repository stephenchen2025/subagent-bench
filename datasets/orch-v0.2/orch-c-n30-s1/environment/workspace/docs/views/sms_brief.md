# Sms Brief view

Module: `views/sms_brief.py`. Audience: mobile users.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0899 | rebuild-feed | done | high | `rebuild-feed (job-0899) is done ***` |
| job-0856 | export-ledger | failed | normal | `export-ledger (job-0856) is failed **` |
| job-0408 | rebuild-feed | running | low | `rebuild-feed (job-0408) is running *` |
| job-0315 | send-digest | failed | normal | `send-digest (job-0315) is failed **` |
| job-0411 | invoice-run | pending | high | `invoice-run (job-0411) is pending ***` |
| job-0511 | sync-inventory | done | low | `sync-inventory (job-0511) is done *` |
| job-0133 | reindex-search | pending | high | `reindex-search (job-0133) is pending ***` |
| job-0679 | sync-inventory | pending | high | `sync-inventory (job-0679) is pending ***` |
| job-0165 | compact-logs | failed | low | `compact-logs (job-0165) is failed *` |
| job-0945 | sync-inventory | running | normal | `sync-inventory (job-0945) is running **` |
| job-0523 | nightly-backup | failed | normal | `nightly-backup (job-0523) is failed **` |
| job-0423 | resize-images | pending | high | `resize-images (job-0423) is pending ***` |
| job-0511 | nightly-backup | failed | normal | `nightly-backup (job-0511) is failed **` |
| job-0564 | compact-logs | done | normal | `compact-logs (job-0564) is done **` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
