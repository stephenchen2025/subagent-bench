# Printer Slip view

Module: `views/printer_slip.py`. Audience: auditors reviewing job history.

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
| job-0335 | invoice-run | pending | low | `vv job-0335: invoice-run -- pending` |
| job-0042 | renew-certs | done | low | `vv job-0042: renew-certs -- done` |
| job-0990 | renew-certs | pending | high | `^^ job-0990: renew-certs -- pending` |
| job-0423 | nightly-backup | running | normal | `-- job-0423: nightly-backup -- running` |
| job-0880 | invoice-run | failed | normal | `-- job-0880: invoice-run -- failed` |
| job-0806 | sync-inventory | failed | low | `vv job-0806: sync-inventory -- failed` |
| job-0292 | invoice-run | failed | low | `vv job-0292: invoice-run -- failed` |
| job-0201 | export-ledger | running | high | `^^ job-0201: export-ledger -- running` |
| job-0708 | sync-inventory | running | high | `^^ job-0708: sync-inventory -- running` |
| job-0804 | rotate-keys | done | low | `vv job-0804: rotate-keys -- done` |
| job-0313 | send-digest | running | high | `^^ job-0313: send-digest -- running` |
| job-0873 | invoice-run | pending | low | `vv job-0873: invoice-run -- pending` |
| job-0781 | compact-logs | failed | normal | `-- job-0781: compact-logs -- failed` |
| job-0865 | export-ledger | pending | high | `^^ job-0865: export-ledger -- pending` |

## History

- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
