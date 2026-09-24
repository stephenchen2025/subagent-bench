# Printer Slip view

Module: `views/printer_slip.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0098 | sync-inventory | failed | high | `!!! job job-0098 / sync-inventory / failed` |
| job-0410 | rotate-keys | pending | low | `! job job-0410 / rotate-keys / pending` |
| job-0285 | invoice-run | running | normal | `!! job job-0285 / invoice-run / running` |
| job-0278 | renew-certs | done | high | `!!! job job-0278 / renew-certs / done` |
| job-0950 | send-digest | running | high | `!!! job job-0950 / send-digest / running` |
| job-0324 | export-ledger | pending | normal | `!! job job-0324 / export-ledger / pending` |
| job-0664 | sync-inventory | failed | high | `!!! job job-0664 / sync-inventory / failed` |
| job-0282 | resize-images | failed | low | `! job job-0282 / resize-images / failed` |
| job-0273 | compact-logs | failed | normal | `!! job job-0273 / compact-logs / failed` |
| job-0135 | export-ledger | pending | normal | `!! job job-0135 / export-ledger / pending` |
| job-0327 | reindex-search | running | low | `! job job-0327 / reindex-search / running` |
| job-0837 | reindex-search | running | high | `!!! job job-0837 / reindex-search / running` |
| job-0957 | rotate-keys | running | high | `!!! job job-0957 / rotate-keys / running` |
| job-0155 | nightly-backup | failed | high | `!!! job job-0155 / nightly-backup / failed` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
