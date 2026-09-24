# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0303 | renew-certs | done | high | `priority:high job-0303: renew-certs -- done` |
| job-0193 | nightly-backup | failed | low | `priority:low job-0193: nightly-backup -- failed` |
| job-0046 | rebuild-feed | pending | low | `priority:low job-0046: rebuild-feed -- pending` |
| job-0898 | nightly-backup | done | low | `priority:low job-0898: nightly-backup -- done` |
| job-0112 | reindex-search | done | low | `priority:low job-0112: reindex-search -- done` |
| job-0417 | nightly-backup | failed | normal | `priority:normal job-0417: nightly-backup -- failed` |
| job-0964 | rebuild-feed | done | high | `priority:high job-0964: rebuild-feed -- done` |
| job-0877 | purge-cache | failed | high | `priority:high job-0877: purge-cache -- failed` |
| job-0106 | compact-logs | done | normal | `priority:normal job-0106: compact-logs -- done` |
| job-0019 | renew-certs | done | low | `priority:low job-0019: renew-certs -- done` |
| job-0059 | nightly-backup | done | low | `priority:low job-0059: nightly-backup -- done` |
| job-0087 | invoice-run | failed | high | `priority:high job-0087: invoice-run -- failed` |
| job-0158 | purge-cache | running | high | `priority:high job-0158: purge-cache -- running` |
| job-0247 | resize-images | pending | low | `priority:low job-0247: resize-images -- pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
