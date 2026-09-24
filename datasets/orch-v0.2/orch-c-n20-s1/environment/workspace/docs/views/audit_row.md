# Audit Row view

Module: `views/audit_row.py`. Audience: release managers.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0566 | export-ledger | pending | high | `^^ PENDING: export-ledger [job-0566]` |
| job-0831 | rebuild-feed | done | high | `^^ DONE: rebuild-feed [job-0831]` |
| job-0146 | purge-cache | pending | low | `vv PENDING: purge-cache [job-0146]` |
| job-0516 | invoice-run | failed | high | `^^ FAILED: invoice-run [job-0516]` |
| job-0113 | reindex-search | failed | normal | `-- FAILED: reindex-search [job-0113]` |
| job-0726 | invoice-run | done | high | `^^ DONE: invoice-run [job-0726]` |
| job-0053 | sync-inventory | failed | normal | `-- FAILED: sync-inventory [job-0053]` |
| job-0900 | export-ledger | failed | normal | `-- FAILED: export-ledger [job-0900]` |
| job-0820 | invoice-run | pending | low | `vv PENDING: invoice-run [job-0820]` |
| job-0922 | rotate-keys | failed | low | `vv FAILED: rotate-keys [job-0922]` |
| job-0629 | invoice-run | done | normal | `-- DONE: invoice-run [job-0629]` |
| job-0882 | compact-logs | failed | high | `^^ FAILED: compact-logs [job-0882]` |
| job-0746 | purge-cache | pending | high | `^^ PENDING: purge-cache [job-0746]` |
| job-0045 | invoice-run | running | high | `^^ RUNNING: invoice-run [job-0045]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
