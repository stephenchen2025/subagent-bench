# Sla Board view

Module: `views/sla_board.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0167 | renew-certs | pending | normal | `job-0167: renew-certs -- pending **` |
| job-0838 | renew-certs | pending | low | `job-0838: renew-certs -- pending *` |
| job-0235 | sync-inventory | pending | high | `job-0235: sync-inventory -- pending ***` |
| job-0594 | purge-cache | pending | high | `job-0594: purge-cache -- pending ***` |
| job-0419 | compact-logs | running | high | `job-0419: compact-logs -- running ***` |
| job-0438 | purge-cache | running | normal | `job-0438: purge-cache -- running **` |
| job-0425 | nightly-backup | done | high | `job-0425: nightly-backup -- done ***` |
| job-0016 | invoice-run | pending | high | `job-0016: invoice-run -- pending ***` |
| job-0022 | compact-logs | pending | normal | `job-0022: compact-logs -- pending **` |
| job-0050 | export-ledger | done | normal | `job-0050: export-ledger -- done **` |
| job-0339 | send-digest | done | low | `job-0339: send-digest -- done *` |
| job-0766 | nightly-backup | pending | high | `job-0766: nightly-backup -- pending ***` |
| job-0843 | nightly-backup | done | high | `job-0843: nightly-backup -- done ***` |
| job-0683 | resize-images | done | normal | `job-0683: resize-images -- done **` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
