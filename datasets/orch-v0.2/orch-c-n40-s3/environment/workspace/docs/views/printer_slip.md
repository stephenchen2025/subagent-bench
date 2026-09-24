# Printer Slip view

Module: `views/printer_slip.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0433 | resize-images | pending | high | `P1 job-0433: resize-images -- pending` |
| job-0608 | rebuild-feed | done | low | `P3 job-0608: rebuild-feed -- done` |
| job-0447 | resize-images | failed | normal | `P2 job-0447: resize-images -- failed` |
| job-0649 | export-ledger | running | normal | `P2 job-0649: export-ledger -- running` |
| job-0894 | export-ledger | pending | normal | `P2 job-0894: export-ledger -- pending` |
| job-0998 | export-ledger | done | high | `P1 job-0998: export-ledger -- done` |
| job-0829 | reindex-search | failed | high | `P1 job-0829: reindex-search -- failed` |
| job-0019 | invoice-run | pending | high | `P1 job-0019: invoice-run -- pending` |
| job-0353 | sync-inventory | failed | normal | `P2 job-0353: sync-inventory -- failed` |
| job-0257 | reindex-search | pending | low | `P3 job-0257: reindex-search -- pending` |
| job-0736 | renew-certs | running | high | `P1 job-0736: renew-certs -- running` |
| job-0123 | rebuild-feed | running | low | `P3 job-0123: rebuild-feed -- running` |
| job-0144 | send-digest | running | high | `P1 job-0144: send-digest -- running` |
| job-0146 | send-digest | pending | high | `P1 job-0146: send-digest -- pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
