# Calendar Note view

Module: `views/calendar_note.py`. Audience: the executive summary email.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0111 | sync-inventory | done | high | `[HIGH] sync-inventory (job-0111) is done` |
| job-0725 | invoice-run | failed | low | `[LOW] invoice-run (job-0725) is failed` |
| job-0802 | rebuild-feed | done | low | `[LOW] rebuild-feed (job-0802) is done` |
| job-0350 | compact-logs | running | high | `[HIGH] compact-logs (job-0350) is running` |
| job-0700 | reindex-search | failed | high | `[HIGH] reindex-search (job-0700) is failed` |
| job-0998 | compact-logs | failed | low | `[LOW] compact-logs (job-0998) is failed` |
| job-0480 | purge-cache | done | high | `[HIGH] purge-cache (job-0480) is done` |
| job-0117 | nightly-backup | failed | normal | `[NORMAL] nightly-backup (job-0117) is failed` |
| job-0527 | send-digest | failed | low | `[LOW] send-digest (job-0527) is failed` |
| job-0243 | export-ledger | pending | normal | `[NORMAL] export-ledger (job-0243) is pending` |
| job-0541 | invoice-run | done | normal | `[NORMAL] invoice-run (job-0541) is done` |
| job-0456 | renew-certs | failed | low | `[LOW] renew-certs (job-0456) is failed` |
| job-0881 | resize-images | done | normal | `[NORMAL] resize-images (job-0881) is done` |
| job-0470 | sync-inventory | running | high | `[HIGH] sync-inventory (job-0470) is running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
