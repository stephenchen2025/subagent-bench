# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the platform team's wall display.

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
| job-0127 | invoice-run | pending | normal | `** job-0127: invoice-run -- pending` |
| job-0987 | compact-logs | done | normal | `** job-0987: compact-logs -- done` |
| job-0435 | send-digest | done | low | `* job-0435: send-digest -- done` |
| job-0627 | sync-inventory | done | high | `*** job-0627: sync-inventory -- done` |
| job-0162 | renew-certs | running | low | `* job-0162: renew-certs -- running` |
| job-0858 | rebuild-feed | failed | low | `* job-0858: rebuild-feed -- failed` |
| job-0326 | resize-images | failed | low | `* job-0326: resize-images -- failed` |
| job-0989 | rotate-keys | failed | low | `* job-0989: rotate-keys -- failed` |
| job-0675 | sync-inventory | pending | low | `* job-0675: sync-inventory -- pending` |
| job-0066 | rotate-keys | done | normal | `** job-0066: rotate-keys -- done` |
| job-0747 | invoice-run | failed | low | `* job-0747: invoice-run -- failed` |
| job-0633 | send-digest | running | low | `* job-0633: send-digest -- running` |
| job-0093 | rebuild-feed | running | normal | `** job-0093: rebuild-feed -- running` |
| job-0717 | rotate-keys | failed | high | `*** job-0717: rotate-keys -- failed` |

## History

- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
