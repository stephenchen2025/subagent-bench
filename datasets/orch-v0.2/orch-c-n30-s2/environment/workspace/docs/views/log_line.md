# Log Line view

Module: `views/log_line.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0428 | reindex-search | failed | high | `URGENT FAILED: reindex-search [job-0428]` |
| job-0240 | invoice-run | done | high | `URGENT DONE: invoice-run [job-0240]` |
| job-0306 | rotate-keys | failed | low | `DEFERRABLE FAILED: rotate-keys [job-0306]` |
| job-0109 | send-digest | done | low | `DEFERRABLE DONE: send-digest [job-0109]` |
| job-0380 | send-digest | done | high | `URGENT DONE: send-digest [job-0380]` |
| job-0711 | sync-inventory | failed | normal | `ROUTINE FAILED: sync-inventory [job-0711]` |
| job-0395 | rotate-keys | pending | high | `URGENT PENDING: rotate-keys [job-0395]` |
| job-0565 | renew-certs | failed | high | `URGENT FAILED: renew-certs [job-0565]` |
| job-0930 | rotate-keys | running | low | `DEFERRABLE RUNNING: rotate-keys [job-0930]` |
| job-0135 | sync-inventory | done | high | `URGENT DONE: sync-inventory [job-0135]` |
| job-0031 | rotate-keys | failed | low | `DEFERRABLE FAILED: rotate-keys [job-0031]` |
| job-0547 | reindex-search | running | normal | `ROUTINE RUNNING: reindex-search [job-0547]` |
| job-0476 | purge-cache | pending | normal | `ROUTINE PENDING: purge-cache [job-0476]` |
| job-0387 | export-ledger | running | low | `DEFERRABLE RUNNING: export-ledger [job-0387]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
