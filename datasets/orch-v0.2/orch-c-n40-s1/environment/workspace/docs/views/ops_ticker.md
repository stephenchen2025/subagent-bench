# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0656 | compact-logs | failed | low | `* job-0656: compact-logs -- failed` |
| job-0237 | reindex-search | failed | normal | `** job-0237: reindex-search -- failed` |
| job-0062 | send-digest | running | high | `*** job-0062: send-digest -- running` |
| job-0300 | resize-images | done | high | `*** job-0300: resize-images -- done` |
| job-0018 | invoice-run | failed | high | `*** job-0018: invoice-run -- failed` |
| job-0205 | compact-logs | pending | normal | `** job-0205: compact-logs -- pending` |
| job-0312 | nightly-backup | running | normal | `** job-0312: nightly-backup -- running` |
| job-0915 | invoice-run | running | high | `*** job-0915: invoice-run -- running` |
| job-0411 | send-digest | done | high | `*** job-0411: send-digest -- done` |
| job-0431 | purge-cache | done | high | `*** job-0431: purge-cache -- done` |
| job-0773 | renew-certs | running | low | `* job-0773: renew-certs -- running` |
| job-0749 | send-digest | failed | low | `* job-0749: send-digest -- failed` |
| job-0959 | rotate-keys | done | normal | `** job-0959: rotate-keys -- done` |
| job-0675 | sync-inventory | failed | normal | `** job-0675: sync-inventory -- failed` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
