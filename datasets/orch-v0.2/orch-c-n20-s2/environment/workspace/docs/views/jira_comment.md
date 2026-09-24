# Jira Comment view

Module: `views/jira_comment.py`. Audience: release managers.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0374 | purge-cache | running | high | `job-0374: purge-cache -- running [HIGH]` |
| job-0711 | compact-logs | running | normal | `job-0711: compact-logs -- running [NORMAL]` |
| job-0588 | sync-inventory | pending | high | `job-0588: sync-inventory -- pending [HIGH]` |
| job-0511 | export-ledger | pending | low | `job-0511: export-ledger -- pending [LOW]` |
| job-0072 | purge-cache | failed | high | `job-0072: purge-cache -- failed [HIGH]` |
| job-0535 | rebuild-feed | running | normal | `job-0535: rebuild-feed -- running [NORMAL]` |
| job-0662 | compact-logs | pending | low | `job-0662: compact-logs -- pending [LOW]` |
| job-0047 | renew-certs | done | low | `job-0047: renew-certs -- done [LOW]` |
| job-0118 | invoice-run | running | high | `job-0118: invoice-run -- running [HIGH]` |
| job-0499 | renew-certs | running | low | `job-0499: renew-certs -- running [LOW]` |
| job-0403 | send-digest | running | normal | `job-0403: send-digest -- running [NORMAL]` |
| job-0487 | compact-logs | pending | low | `job-0487: compact-logs -- pending [LOW]` |
| job-0063 | compact-logs | failed | high | `job-0063: compact-logs -- failed [HIGH]` |
| job-0672 | rotate-keys | failed | low | `job-0672: rotate-keys -- failed [LOW]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
