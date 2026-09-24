# Printer Slip view

Module: `views/printer_slip.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0728 | renew-certs | running | normal | `RUNNING: renew-certs [job-0728] P2` |
| job-0493 | renew-certs | done | high | `DONE: renew-certs [job-0493] P1` |
| job-0225 | export-ledger | pending | high | `PENDING: export-ledger [job-0225] P1` |
| job-0828 | send-digest | pending | normal | `PENDING: send-digest [job-0828] P2` |
| job-0676 | purge-cache | failed | low | `FAILED: purge-cache [job-0676] P3` |
| job-0273 | rotate-keys | running | high | `RUNNING: rotate-keys [job-0273] P1` |
| job-0610 | renew-certs | done | normal | `DONE: renew-certs [job-0610] P2` |
| job-0439 | purge-cache | failed | normal | `FAILED: purge-cache [job-0439] P2` |
| job-0804 | resize-images | failed | low | `FAILED: resize-images [job-0804] P3` |
| job-0911 | resize-images | running | high | `RUNNING: resize-images [job-0911] P1` |
| job-0537 | reindex-search | done | high | `DONE: reindex-search [job-0537] P1` |
| job-0204 | purge-cache | pending | normal | `PENDING: purge-cache [job-0204] P2` |
| job-0264 | purge-cache | failed | normal | `FAILED: purge-cache [job-0264] P2` |
| job-0588 | nightly-backup | pending | normal | `PENDING: nightly-backup [job-0588] P2` |

## History

- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
