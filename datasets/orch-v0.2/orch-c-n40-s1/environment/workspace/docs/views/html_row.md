# Html Row view

Module: `views/html_row.py`. Audience: customer support leads.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0715 | renew-certs | running | high | `P1 job-0715: renew-certs -- running` |
| job-0270 | reindex-search | running | high | `P1 job-0270: reindex-search -- running` |
| job-0964 | send-digest | failed | normal | `P2 job-0964: send-digest -- failed` |
| job-0746 | rebuild-feed | failed | normal | `P2 job-0746: rebuild-feed -- failed` |
| job-0144 | export-ledger | failed | high | `P1 job-0144: export-ledger -- failed` |
| job-0737 | rebuild-feed | failed | low | `P3 job-0737: rebuild-feed -- failed` |
| job-0465 | compact-logs | done | normal | `P2 job-0465: compact-logs -- done` |
| job-0923 | purge-cache | running | low | `P3 job-0923: purge-cache -- running` |
| job-0439 | nightly-backup | failed | high | `P1 job-0439: nightly-backup -- failed` |
| job-0769 | sync-inventory | done | low | `P3 job-0769: sync-inventory -- done` |
| job-0528 | renew-certs | failed | low | `P3 job-0528: renew-certs -- failed` |
| job-0100 | rotate-keys | pending | normal | `P2 job-0100: rotate-keys -- pending` |
| job-0076 | resize-images | pending | high | `P1 job-0076: resize-images -- pending` |
| job-0769 | rotate-keys | pending | normal | `P2 job-0769: rotate-keys -- pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
