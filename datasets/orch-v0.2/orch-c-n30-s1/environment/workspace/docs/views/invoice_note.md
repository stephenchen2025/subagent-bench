# Invoice Note view

Module: `views/invoice_note.py`. Audience: the platform team's wall display.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0728 | rebuild-feed | pending | high | `job-0728: rebuild-feed -- pending !!!` |
| job-0403 | nightly-backup | pending | high | `job-0403: nightly-backup -- pending !!!` |
| job-0397 | compact-logs | done | normal | `job-0397: compact-logs -- done !!` |
| job-0837 | nightly-backup | pending | low | `job-0837: nightly-backup -- pending !` |
| job-0418 | send-digest | pending | normal | `job-0418: send-digest -- pending !!` |
| job-0459 | export-ledger | failed | high | `job-0459: export-ledger -- failed !!!` |
| job-0359 | renew-certs | pending | low | `job-0359: renew-certs -- pending !` |
| job-0655 | sync-inventory | done | high | `job-0655: sync-inventory -- done !!!` |
| job-0527 | resize-images | pending | normal | `job-0527: resize-images -- pending !!` |
| job-0274 | sync-inventory | done | normal | `job-0274: sync-inventory -- done !!` |
| job-0077 | export-ledger | running | normal | `job-0077: export-ledger -- running !!` |
| job-0045 | export-ledger | done | high | `job-0045: export-ledger -- done !!!` |
| job-0274 | sync-inventory | failed | high | `job-0274: sync-inventory -- failed !!!` |
| job-0247 | export-ledger | running | low | `job-0247: export-ledger -- running !` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
