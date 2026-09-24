# Grafana Note view

Module: `views/grafana_note.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0987 | compact-logs | pending | normal | `job-0987: compact-logs -- pending [NORMAL]` |
| job-0625 | send-digest | running | high | `job-0625: send-digest -- running [HIGH]` |
| job-0943 | export-ledger | running | normal | `job-0943: export-ledger -- running [NORMAL]` |
| job-0266 | compact-logs | failed | normal | `job-0266: compact-logs -- failed [NORMAL]` |
| job-0546 | invoice-run | done | high | `job-0546: invoice-run -- done [HIGH]` |
| job-0683 | sync-inventory | done | low | `job-0683: sync-inventory -- done [LOW]` |
| job-0356 | purge-cache | pending | high | `job-0356: purge-cache -- pending [HIGH]` |
| job-0548 | rebuild-feed | running | normal | `job-0548: rebuild-feed -- running [NORMAL]` |
| job-0743 | sync-inventory | running | high | `job-0743: sync-inventory -- running [HIGH]` |
| job-0377 | nightly-backup | pending | normal | `job-0377: nightly-backup -- pending [NORMAL]` |
| job-0157 | rotate-keys | running | high | `job-0157: rotate-keys -- running [HIGH]` |
| job-0933 | send-digest | running | low | `job-0933: send-digest -- running [LOW]` |
| job-0569 | renew-certs | done | normal | `job-0569: renew-certs -- done [NORMAL]` |
| job-0480 | resize-images | running | normal | `job-0480: resize-images -- running [NORMAL]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
