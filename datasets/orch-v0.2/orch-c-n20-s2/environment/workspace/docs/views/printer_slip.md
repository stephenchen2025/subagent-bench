# Printer Slip view

Module: `views/printer_slip.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0703 | compact-logs | done | high | `DONE: compact-logs [job-0703] color=red` |
| job-0096 | rotate-keys | running | high | `RUNNING: rotate-keys [job-0096] color=red` |
| job-0021 | purge-cache | done | low | `DONE: purge-cache [job-0021] color=green` |
| job-0509 | reindex-search | failed | normal | `FAILED: reindex-search [job-0509] color=amber` |
| job-0542 | export-ledger | pending | high | `PENDING: export-ledger [job-0542] color=red` |
| job-0946 | reindex-search | pending | normal | `PENDING: reindex-search [job-0946] color=amber` |
| job-0488 | renew-certs | failed | high | `FAILED: renew-certs [job-0488] color=red` |
| job-0032 | sync-inventory | done | normal | `DONE: sync-inventory [job-0032] color=amber` |
| job-0394 | invoice-run | running | low | `RUNNING: invoice-run [job-0394] color=green` |
| job-0245 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0245] color=green` |
| job-0057 | export-ledger | failed | low | `FAILED: export-ledger [job-0057] color=green` |
| job-0963 | resize-images | running | low | `RUNNING: resize-images [job-0963] color=green` |
| job-0383 | sync-inventory | done | high | `DONE: sync-inventory [job-0383] color=red` |
| job-0052 | sync-inventory | running | normal | `RUNNING: sync-inventory [job-0052] color=amber` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
