# Mobile Push view

Module: `views/mobile_push.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0275 | export-ledger | failed | low | `! job job-0275 / export-ledger / failed` |
| job-0549 | purge-cache | done | high | `!!! job job-0549 / purge-cache / done` |
| job-0083 | invoice-run | pending | low | `! job job-0083 / invoice-run / pending` |
| job-0633 | send-digest | done | high | `!!! job job-0633 / send-digest / done` |
| job-0400 | rotate-keys | running | low | `! job job-0400 / rotate-keys / running` |
| job-0368 | compact-logs | failed | low | `! job job-0368 / compact-logs / failed` |
| job-0792 | nightly-backup | pending | normal | `!! job job-0792 / nightly-backup / pending` |
| job-0694 | export-ledger | failed | high | `!!! job job-0694 / export-ledger / failed` |
| job-0293 | send-digest | done | high | `!!! job job-0293 / send-digest / done` |
| job-0995 | renew-certs | pending | high | `!!! job job-0995 / renew-certs / pending` |
| job-0220 | resize-images | done | low | `! job job-0220 / resize-images / done` |
| job-0329 | renew-certs | running | low | `! job job-0329 / renew-certs / running` |
| job-0044 | rotate-keys | failed | low | `! job job-0044 / rotate-keys / failed` |
| job-0630 | invoice-run | done | high | `!!! job job-0630 / invoice-run / done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
