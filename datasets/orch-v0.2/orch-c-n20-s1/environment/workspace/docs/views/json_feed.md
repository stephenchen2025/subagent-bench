# Json Feed view

Module: `views/json_feed.py`. Audience: customer support leads.

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
| job-0882 | nightly-backup | failed | normal | `ROUTINE job-0882: nightly-backup -- failed` |
| job-0125 | renew-certs | pending | high | `URGENT job-0125: renew-certs -- pending` |
| job-0329 | export-ledger | done | high | `URGENT job-0329: export-ledger -- done` |
| job-0509 | nightly-backup | done | normal | `ROUTINE job-0509: nightly-backup -- done` |
| job-0286 | invoice-run | failed | low | `DEFERRABLE job-0286: invoice-run -- failed` |
| job-0685 | invoice-run | failed | high | `URGENT job-0685: invoice-run -- failed` |
| job-0748 | nightly-backup | failed | low | `DEFERRABLE job-0748: nightly-backup -- failed` |
| job-0739 | resize-images | pending | normal | `ROUTINE job-0739: resize-images -- pending` |
| job-0279 | invoice-run | pending | high | `URGENT job-0279: invoice-run -- pending` |
| job-0759 | renew-certs | failed | high | `URGENT job-0759: renew-certs -- failed` |
| job-0496 | purge-cache | done | high | `URGENT job-0496: purge-cache -- done` |
| job-0519 | reindex-search | done | normal | `ROUTINE job-0519: reindex-search -- done` |
| job-0716 | sync-inventory | pending | high | `URGENT job-0716: sync-inventory -- pending` |
| job-0745 | compact-logs | pending | normal | `ROUTINE job-0745: compact-logs -- pending` |

## History

- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
