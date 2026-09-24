# Tv Wall view

Module: `views/tv_wall.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0883 | renew-certs | failed | high | `!!! job-0883: renew-certs -- failed` |
| job-0178 | send-digest | failed | high | `!!! job-0178: send-digest -- failed` |
| job-0427 | renew-certs | running | high | `!!! job-0427: renew-certs -- running` |
| job-0314 | nightly-backup | done | normal | `!! job-0314: nightly-backup -- done` |
| job-0993 | resize-images | failed | low | `! job-0993: resize-images -- failed` |
| job-0527 | rotate-keys | pending | low | `! job-0527: rotate-keys -- pending` |
| job-0510 | compact-logs | done | low | `! job-0510: compact-logs -- done` |
| job-0615 | send-digest | pending | high | `!!! job-0615: send-digest -- pending` |
| job-0085 | rebuild-feed | done | high | `!!! job-0085: rebuild-feed -- done` |
| job-0729 | export-ledger | done | normal | `!! job-0729: export-ledger -- done` |
| job-0606 | sync-inventory | pending | high | `!!! job-0606: sync-inventory -- pending` |
| job-0872 | rebuild-feed | failed | normal | `!! job-0872: rebuild-feed -- failed` |
| job-0689 | renew-certs | pending | high | `!!! job-0689: renew-certs -- pending` |
| job-0255 | nightly-backup | running | normal | `!! job-0255: nightly-backup -- running` |

## History

- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
