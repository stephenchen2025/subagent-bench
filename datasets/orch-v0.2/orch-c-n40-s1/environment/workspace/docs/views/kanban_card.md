# Kanban Card view

Module: `views/kanban_card.py`. Audience: customer support leads.

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
| job-0560 | reindex-search | done | low | `* job-0560: reindex-search -- done` |
| job-0091 | purge-cache | running | high | `*** job-0091: purge-cache -- running` |
| job-0405 | nightly-backup | done | high | `*** job-0405: nightly-backup -- done` |
| job-0664 | send-digest | done | high | `*** job-0664: send-digest -- done` |
| job-0730 | invoice-run | pending | normal | `** job-0730: invoice-run -- pending` |
| job-0097 | rebuild-feed | running | high | `*** job-0097: rebuild-feed -- running` |
| job-0888 | reindex-search | failed | low | `* job-0888: reindex-search -- failed` |
| job-0789 | resize-images | failed | high | `*** job-0789: resize-images -- failed` |
| job-0581 | resize-images | failed | normal | `** job-0581: resize-images -- failed` |
| job-0083 | invoice-run | pending | high | `*** job-0083: invoice-run -- pending` |
| job-0399 | purge-cache | done | normal | `** job-0399: purge-cache -- done` |
| job-0505 | export-ledger | done | low | `* job-0505: export-ledger -- done` |
| job-0958 | sync-inventory | pending | high | `*** job-0958: sync-inventory -- pending` |
| job-0853 | renew-certs | failed | high | `*** job-0853: renew-certs -- failed` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
