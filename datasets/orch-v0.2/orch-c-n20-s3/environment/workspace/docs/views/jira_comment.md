# Jira Comment view

Module: `views/jira_comment.py`. Audience: customer support leads.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0233 | export-ledger | done | normal | `job-0233: export-ledger -- done ROUTINE` |
| job-0658 | send-digest | running | low | `job-0658: send-digest -- running DEFERRABLE` |
| job-0263 | sync-inventory | done | normal | `job-0263: sync-inventory -- done ROUTINE` |
| job-0047 | renew-certs | failed | low | `job-0047: renew-certs -- failed DEFERRABLE` |
| job-0703 | invoice-run | running | high | `job-0703: invoice-run -- running URGENT` |
| job-0893 | purge-cache | done | low | `job-0893: purge-cache -- done DEFERRABLE` |
| job-0522 | export-ledger | pending | high | `job-0522: export-ledger -- pending URGENT` |
| job-0301 | resize-images | failed | low | `job-0301: resize-images -- failed DEFERRABLE` |
| job-0632 | rotate-keys | pending | normal | `job-0632: rotate-keys -- pending ROUTINE` |
| job-0987 | nightly-backup | pending | high | `job-0987: nightly-backup -- pending URGENT` |
| job-0715 | invoice-run | running | low | `job-0715: invoice-run -- running DEFERRABLE` |
| job-0032 | rotate-keys | done | low | `job-0032: rotate-keys -- done DEFERRABLE` |
| job-0814 | invoice-run | pending | high | `job-0814: invoice-run -- pending URGENT` |
| job-0417 | rotate-keys | pending | normal | `job-0417: rotate-keys -- pending ROUTINE` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
