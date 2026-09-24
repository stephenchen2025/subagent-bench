# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: customer support leads.

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
| job-0263 | rotate-keys | done | high | `job-0263: rotate-keys -- done ^^` |
| job-0277 | invoice-run | pending | normal | `job-0277: invoice-run -- pending --` |
| job-0005 | sync-inventory | done | normal | `job-0005: sync-inventory -- done --` |
| job-0808 | rebuild-feed | failed | low | `job-0808: rebuild-feed -- failed vv` |
| job-0398 | rebuild-feed | running | high | `job-0398: rebuild-feed -- running ^^` |
| job-0509 | send-digest | failed | normal | `job-0509: send-digest -- failed --` |
| job-0569 | resize-images | pending | high | `job-0569: resize-images -- pending ^^` |
| job-0267 | invoice-run | done | normal | `job-0267: invoice-run -- done --` |
| job-0470 | purge-cache | running | low | `job-0470: purge-cache -- running vv` |
| job-0843 | send-digest | running | low | `job-0843: send-digest -- running vv` |
| job-0642 | renew-certs | done | low | `job-0642: renew-certs -- done vv` |
| job-0441 | compact-logs | running | high | `job-0441: compact-logs -- running ^^` |
| job-0953 | export-ledger | pending | low | `job-0953: export-ledger -- pending vv` |
| job-0667 | compact-logs | pending | normal | `job-0667: compact-logs -- pending --` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
