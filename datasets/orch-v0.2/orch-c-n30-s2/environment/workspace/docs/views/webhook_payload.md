# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the platform team's wall display.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0980 | export-ledger | running | normal | `color=amber job-0980: export-ledger -- running` |
| job-0836 | invoice-run | running | low | `color=green job-0836: invoice-run -- running` |
| job-0544 | compact-logs | failed | low | `color=green job-0544: compact-logs -- failed` |
| job-0103 | rotate-keys | running | low | `color=green job-0103: rotate-keys -- running` |
| job-0537 | compact-logs | running | high | `color=red job-0537: compact-logs -- running` |
| job-0041 | sync-inventory | running | normal | `color=amber job-0041: sync-inventory -- running` |
| job-0685 | rotate-keys | pending | low | `color=green job-0685: rotate-keys -- pending` |
| job-0703 | invoice-run | running | normal | `color=amber job-0703: invoice-run -- running` |
| job-0507 | sync-inventory | failed | high | `color=red job-0507: sync-inventory -- failed` |
| job-0414 | nightly-backup | failed | low | `color=green job-0414: nightly-backup -- failed` |
| job-0450 | invoice-run | done | high | `color=red job-0450: invoice-run -- done` |
| job-0545 | renew-certs | done | normal | `color=amber job-0545: renew-certs -- done` |
| job-0383 | nightly-backup | pending | normal | `color=amber job-0383: nightly-backup -- pending` |
| job-0745 | rebuild-feed | running | normal | `color=amber job-0745: rebuild-feed -- running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
