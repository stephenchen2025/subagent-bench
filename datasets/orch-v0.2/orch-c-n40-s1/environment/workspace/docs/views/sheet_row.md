# Sheet Row view

Module: `views/sheet_row.py`. Audience: the executive summary email.

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
| job-0924 | rotate-keys | failed | low | `DEFERRABLE rotate-keys (job-0924) is failed` |
| job-0228 | invoice-run | pending | high | `URGENT invoice-run (job-0228) is pending` |
| job-0321 | send-digest | done | low | `DEFERRABLE send-digest (job-0321) is done` |
| job-0327 | renew-certs | done | high | `URGENT renew-certs (job-0327) is done` |
| job-0139 | rebuild-feed | running | normal | `ROUTINE rebuild-feed (job-0139) is running` |
| job-0590 | reindex-search | failed | low | `DEFERRABLE reindex-search (job-0590) is failed` |
| job-0993 | sync-inventory | done | high | `URGENT sync-inventory (job-0993) is done` |
| job-0012 | export-ledger | done | normal | `ROUTINE export-ledger (job-0012) is done` |
| job-0898 | resize-images | running | high | `URGENT resize-images (job-0898) is running` |
| job-0580 | send-digest | done | high | `URGENT send-digest (job-0580) is done` |
| job-0719 | reindex-search | failed | high | `URGENT reindex-search (job-0719) is failed` |
| job-0165 | resize-images | failed | low | `DEFERRABLE resize-images (job-0165) is failed` |
| job-0446 | export-ledger | pending | normal | `ROUTINE export-ledger (job-0446) is pending` |
| job-0854 | send-digest | done | low | `DEFERRABLE send-digest (job-0854) is done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
