# Html Row view

Module: `views/html_row.py`. Audience: release managers.

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
| job-0674 | renew-certs | failed | low | `job-0674: renew-certs -- failed !` |
| job-0444 | rebuild-feed | pending | high | `job-0444: rebuild-feed -- pending !!!` |
| job-0761 | sync-inventory | failed | normal | `job-0761: sync-inventory -- failed !!` |
| job-0015 | nightly-backup | pending | low | `job-0015: nightly-backup -- pending !` |
| job-0308 | send-digest | pending | low | `job-0308: send-digest -- pending !` |
| job-0592 | nightly-backup | pending | high | `job-0592: nightly-backup -- pending !!!` |
| job-0165 | resize-images | done | high | `job-0165: resize-images -- done !!!` |
| job-0197 | renew-certs | done | normal | `job-0197: renew-certs -- done !!` |
| job-0728 | nightly-backup | done | high | `job-0728: nightly-backup -- done !!!` |
| job-0669 | send-digest | failed | low | `job-0669: send-digest -- failed !` |
| job-0811 | compact-logs | failed | low | `job-0811: compact-logs -- failed !` |
| job-0146 | invoice-run | done | normal | `job-0146: invoice-run -- done !!` |
| job-0034 | compact-logs | pending | high | `job-0034: compact-logs -- pending !!!` |
| job-0720 | renew-certs | running | normal | `job-0720: renew-certs -- running !!` |

## History

- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
