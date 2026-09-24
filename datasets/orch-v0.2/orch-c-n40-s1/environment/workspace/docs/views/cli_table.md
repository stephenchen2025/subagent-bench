# Cli Table view

Module: `views/cli_table.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0341 | rotate-keys | running | low | `* RUNNING: rotate-keys [job-0341]` |
| job-0662 | sync-inventory | done | low | `* DONE: sync-inventory [job-0662]` |
| job-0746 | send-digest | pending | low | `* PENDING: send-digest [job-0746]` |
| job-0096 | sync-inventory | failed | low | `* FAILED: sync-inventory [job-0096]` |
| job-0550 | send-digest | pending | low | `* PENDING: send-digest [job-0550]` |
| job-0379 | renew-certs | pending | low | `* PENDING: renew-certs [job-0379]` |
| job-0855 | resize-images | running | low | `* RUNNING: resize-images [job-0855]` |
| job-0433 | send-digest | running | normal | `** RUNNING: send-digest [job-0433]` |
| job-0702 | nightly-backup | pending | normal | `** PENDING: nightly-backup [job-0702]` |
| job-0668 | send-digest | pending | low | `* PENDING: send-digest [job-0668]` |
| job-0918 | send-digest | pending | high | `*** PENDING: send-digest [job-0918]` |
| job-0281 | sync-inventory | pending | normal | `** PENDING: sync-inventory [job-0281]` |
| job-0629 | nightly-backup | done | normal | `** DONE: nightly-backup [job-0629]` |
| job-0785 | invoice-run | done | normal | `** DONE: invoice-run [job-0785]` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
