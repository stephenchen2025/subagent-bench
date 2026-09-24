# Chat Bot view

Module: `views/chat_bot.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0358 | compact-logs | failed | normal | `** job-0358: compact-logs -- failed` |
| job-0963 | invoice-run | done | low | `* job-0963: invoice-run -- done` |
| job-0608 | compact-logs | pending | high | `*** job-0608: compact-logs -- pending` |
| job-0446 | compact-logs | done | low | `* job-0446: compact-logs -- done` |
| job-0429 | renew-certs | failed | high | `*** job-0429: renew-certs -- failed` |
| job-0945 | purge-cache | failed | high | `*** job-0945: purge-cache -- failed` |
| job-0330 | compact-logs | running | low | `* job-0330: compact-logs -- running` |
| job-0351 | send-digest | failed | low | `* job-0351: send-digest -- failed` |
| job-0125 | export-ledger | done | low | `* job-0125: export-ledger -- done` |
| job-0623 | resize-images | failed | low | `* job-0623: resize-images -- failed` |
| job-0805 | export-ledger | running | high | `*** job-0805: export-ledger -- running` |
| job-0187 | sync-inventory | failed | low | `* job-0187: sync-inventory -- failed` |
| job-0481 | reindex-search | done | high | `*** job-0481: reindex-search -- done` |
| job-0073 | renew-certs | running | low | `* job-0073: renew-certs -- running` |

## History

- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
