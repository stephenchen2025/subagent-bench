# Status Badge view

Module: `views/status_badge.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0145 | sync-inventory | running | low | `job-0145: sync-inventory -- running DEFERRABLE` |
| job-0798 | compact-logs | failed | high | `job-0798: compact-logs -- failed URGENT` |
| job-0908 | sync-inventory | pending | low | `job-0908: sync-inventory -- pending DEFERRABLE` |
| job-0363 | export-ledger | pending | high | `job-0363: export-ledger -- pending URGENT` |
| job-0921 | rotate-keys | done | normal | `job-0921: rotate-keys -- done ROUTINE` |
| job-0703 | nightly-backup | failed | normal | `job-0703: nightly-backup -- failed ROUTINE` |
| job-0667 | sync-inventory | done | high | `job-0667: sync-inventory -- done URGENT` |
| job-0803 | purge-cache | failed | high | `job-0803: purge-cache -- failed URGENT` |
| job-0964 | invoice-run | done | normal | `job-0964: invoice-run -- done ROUTINE` |
| job-0135 | rotate-keys | running | high | `job-0135: rotate-keys -- running URGENT` |
| job-0493 | nightly-backup | done | high | `job-0493: nightly-backup -- done URGENT` |
| job-0071 | nightly-backup | failed | normal | `job-0071: nightly-backup -- failed ROUTINE` |
| job-0048 | export-ledger | failed | low | `job-0048: export-ledger -- failed DEFERRABLE` |
| job-0045 | nightly-backup | running | normal | `job-0045: nightly-backup -- running ROUTINE` |

## History

- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
