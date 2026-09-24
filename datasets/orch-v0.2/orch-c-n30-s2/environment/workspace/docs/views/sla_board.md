# Sla Board view

Module: `views/sla_board.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0559 | compact-logs | pending | normal | `job-0559 | compact-logs | pending !!` |
| job-0096 | sync-inventory | pending | low | `job-0096 | sync-inventory | pending !` |
| job-0200 | send-digest | done | high | `job-0200 | send-digest | done !!!` |
| job-0132 | rotate-keys | running | normal | `job-0132 | rotate-keys | running !!` |
| job-0724 | invoice-run | done | normal | `job-0724 | invoice-run | done !!` |
| job-0753 | export-ledger | failed | high | `job-0753 | export-ledger | failed !!!` |
| job-0591 | purge-cache | failed | high | `job-0591 | purge-cache | failed !!!` |
| job-0047 | export-ledger | running | high | `job-0047 | export-ledger | running !!!` |
| job-0353 | renew-certs | failed | normal | `job-0353 | renew-certs | failed !!` |
| job-0472 | purge-cache | pending | normal | `job-0472 | purge-cache | pending !!` |
| job-0443 | export-ledger | done | low | `job-0443 | export-ledger | done !` |
| job-0487 | compact-logs | failed | normal | `job-0487 | compact-logs | failed !!` |
| job-0628 | renew-certs | pending | high | `job-0628 | renew-certs | pending !!!` |
| job-0017 | renew-certs | failed | low | `job-0017 | renew-certs | failed !` |

## History

- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
