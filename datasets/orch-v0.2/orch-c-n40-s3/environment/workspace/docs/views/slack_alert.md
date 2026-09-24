# Slack Alert view

Module: `views/slack_alert.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0759 | resize-images | failed | normal | `ROUTINE job-0759: resize-images -- failed` |
| job-0536 | compact-logs | failed | high | `URGENT job-0536: compact-logs -- failed` |
| job-0231 | purge-cache | done | normal | `ROUTINE job-0231: purge-cache -- done` |
| job-0401 | purge-cache | pending | high | `URGENT job-0401: purge-cache -- pending` |
| job-0156 | export-ledger | pending | low | `DEFERRABLE job-0156: export-ledger -- pending` |
| job-0156 | invoice-run | pending | high | `URGENT job-0156: invoice-run -- pending` |
| job-0495 | resize-images | pending | low | `DEFERRABLE job-0495: resize-images -- pending` |
| job-0265 | purge-cache | done | high | `URGENT job-0265: purge-cache -- done` |
| job-0066 | resize-images | failed | high | `URGENT job-0066: resize-images -- failed` |
| job-0970 | invoice-run | pending | high | `URGENT job-0970: invoice-run -- pending` |
| job-0064 | reindex-search | done | low | `DEFERRABLE job-0064: reindex-search -- done` |
| job-0628 | invoice-run | pending | low | `DEFERRABLE job-0628: invoice-run -- pending` |
| job-0003 | nightly-backup | done | low | `DEFERRABLE job-0003: nightly-backup -- done` |
| job-0245 | resize-images | pending | low | `DEFERRABLE job-0245: resize-images -- pending` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
