# Printer Slip view

Module: `views/printer_slip.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0377 | export-ledger | done | high | `^^ job-0377: export-ledger -- done` |
| job-0343 | purge-cache | pending | high | `^^ job-0343: purge-cache -- pending` |
| job-0119 | sync-inventory | done | normal | `-- job-0119: sync-inventory -- done` |
| job-0699 | renew-certs | done | normal | `-- job-0699: renew-certs -- done` |
| job-0989 | compact-logs | pending | normal | `-- job-0989: compact-logs -- pending` |
| job-0982 | sync-inventory | failed | high | `^^ job-0982: sync-inventory -- failed` |
| job-0322 | send-digest | running | low | `vv job-0322: send-digest -- running` |
| job-0764 | reindex-search | pending | high | `^^ job-0764: reindex-search -- pending` |
| job-0861 | renew-certs | running | high | `^^ job-0861: renew-certs -- running` |
| job-0979 | compact-logs | failed | normal | `-- job-0979: compact-logs -- failed` |
| job-0640 | purge-cache | failed | low | `vv job-0640: purge-cache -- failed` |
| job-0591 | reindex-search | failed | high | `^^ job-0591: reindex-search -- failed` |
| job-0076 | sync-inventory | done | high | `^^ job-0076: sync-inventory -- done` |
| job-0187 | rotate-keys | pending | normal | `-- job-0187: rotate-keys -- pending` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
