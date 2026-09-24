# Chat Bot view

Module: `views/chat_bot.py`. Audience: auditors reviewing job history.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0875 | send-digest | running | normal | `job-0875: send-digest -- running --` |
| job-0737 | sync-inventory | failed | low | `job-0737: sync-inventory -- failed vv` |
| job-0424 | sync-inventory | failed | normal | `job-0424: sync-inventory -- failed --` |
| job-0814 | export-ledger | pending | low | `job-0814: export-ledger -- pending vv` |
| job-0038 | export-ledger | done | normal | `job-0038: export-ledger -- done --` |
| job-0496 | send-digest | failed | normal | `job-0496: send-digest -- failed --` |
| job-0207 | export-ledger | done | high | `job-0207: export-ledger -- done ^^` |
| job-0585 | rebuild-feed | failed | high | `job-0585: rebuild-feed -- failed ^^` |
| job-0253 | nightly-backup | running | low | `job-0253: nightly-backup -- running vv` |
| job-0245 | send-digest | running | high | `job-0245: send-digest -- running ^^` |
| job-0004 | sync-inventory | running | normal | `job-0004: sync-inventory -- running --` |
| job-0224 | nightly-backup | running | low | `job-0224: nightly-backup -- running vv` |
| job-0020 | export-ledger | done | low | `job-0020: export-ledger -- done vv` |
| job-0997 | export-ledger | failed | normal | `job-0997: export-ledger -- failed --` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
