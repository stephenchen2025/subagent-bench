# Html Row view

Module: `views/html_row.py`. Audience: the platform team's wall display.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0260 | compact-logs | failed | normal | `P2 job-0260 | compact-logs | failed` |
| job-0133 | resize-images | pending | high | `P1 job-0133 | resize-images | pending` |
| job-0375 | export-ledger | pending | high | `P1 job-0375 | export-ledger | pending` |
| job-0181 | purge-cache | failed | normal | `P2 job-0181 | purge-cache | failed` |
| job-0488 | export-ledger | done | low | `P3 job-0488 | export-ledger | done` |
| job-0388 | compact-logs | pending | high | `P1 job-0388 | compact-logs | pending` |
| job-0861 | invoice-run | failed | normal | `P2 job-0861 | invoice-run | failed` |
| job-0396 | export-ledger | failed | high | `P1 job-0396 | export-ledger | failed` |
| job-0709 | export-ledger | failed | high | `P1 job-0709 | export-ledger | failed` |
| job-0942 | send-digest | done | low | `P3 job-0942 | send-digest | done` |
| job-0495 | send-digest | done | high | `P1 job-0495 | send-digest | done` |
| job-0155 | renew-certs | done | normal | `P2 job-0155 | renew-certs | done` |
| job-0971 | purge-cache | done | low | `P3 job-0971 | purge-cache | done` |
| job-0187 | export-ledger | running | low | `P3 job-0187 | export-ledger | running` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
