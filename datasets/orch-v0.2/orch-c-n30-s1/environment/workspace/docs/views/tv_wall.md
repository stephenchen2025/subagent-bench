# Tv Wall view

Module: `views/tv_wall.py`. Audience: mobile users.

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
| job-0863 | rotate-keys | pending | high | `URGENT PENDING: rotate-keys [job-0863]` |
| job-0086 | renew-certs | running | normal | `ROUTINE RUNNING: renew-certs [job-0086]` |
| job-0173 | invoice-run | running | normal | `ROUTINE RUNNING: invoice-run [job-0173]` |
| job-0709 | purge-cache | running | normal | `ROUTINE RUNNING: purge-cache [job-0709]` |
| job-0379 | purge-cache | running | low | `DEFERRABLE RUNNING: purge-cache [job-0379]` |
| job-0572 | purge-cache | pending | high | `URGENT PENDING: purge-cache [job-0572]` |
| job-0335 | rotate-keys | running | high | `URGENT RUNNING: rotate-keys [job-0335]` |
| job-0914 | reindex-search | failed | normal | `ROUTINE FAILED: reindex-search [job-0914]` |
| job-0706 | send-digest | running | high | `URGENT RUNNING: send-digest [job-0706]` |
| job-0676 | rotate-keys | pending | high | `URGENT PENDING: rotate-keys [job-0676]` |
| job-0741 | sync-inventory | done | normal | `ROUTINE DONE: sync-inventory [job-0741]` |
| job-0521 | sync-inventory | pending | normal | `ROUTINE PENDING: sync-inventory [job-0521]` |
| job-0687 | invoice-run | pending | low | `DEFERRABLE PENDING: invoice-run [job-0687]` |
| job-0825 | export-ledger | failed | low | `DEFERRABLE FAILED: export-ledger [job-0825]` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
