# Teams Card view

Module: `views/teams_card.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0046 | purge-cache | done | high | `job job-0046 / purge-cache / done ^^` |
| job-0484 | sync-inventory | running | normal | `job job-0484 / sync-inventory / running --` |
| job-0128 | compact-logs | pending | normal | `job job-0128 / compact-logs / pending --` |
| job-0821 | nightly-backup | failed | normal | `job job-0821 / nightly-backup / failed --` |
| job-0933 | sync-inventory | failed | low | `job job-0933 / sync-inventory / failed vv` |
| job-0736 | purge-cache | running | high | `job job-0736 / purge-cache / running ^^` |
| job-0605 | send-digest | done | low | `job job-0605 / send-digest / done vv` |
| job-0940 | compact-logs | failed | low | `job job-0940 / compact-logs / failed vv` |
| job-0310 | sync-inventory | done | low | `job job-0310 / sync-inventory / done vv` |
| job-0551 | sync-inventory | done | normal | `job job-0551 / sync-inventory / done --` |
| job-0788 | rotate-keys | failed | high | `job job-0788 / rotate-keys / failed ^^` |
| job-0570 | nightly-backup | failed | high | `job job-0570 / nightly-backup / failed ^^` |
| job-0710 | renew-certs | failed | high | `job job-0710 / renew-certs / failed ^^` |
| job-0205 | purge-cache | done | high | `job job-0205 / purge-cache / done ^^` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
