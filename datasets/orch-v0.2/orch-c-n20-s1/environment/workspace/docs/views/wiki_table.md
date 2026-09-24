# Wiki Table view

Module: `views/wiki_table.py`. Audience: auditors reviewing job history.

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
| job-0567 | resize-images | done | low | `DEFERRABLE job-0567: resize-images -- done` |
| job-0606 | reindex-search | failed | low | `DEFERRABLE job-0606: reindex-search -- failed` |
| job-0794 | reindex-search | failed | low | `DEFERRABLE job-0794: reindex-search -- failed` |
| job-0264 | rebuild-feed | running | low | `DEFERRABLE job-0264: rebuild-feed -- running` |
| job-0316 | export-ledger | running | high | `URGENT job-0316: export-ledger -- running` |
| job-0486 | invoice-run | running | normal | `ROUTINE job-0486: invoice-run -- running` |
| job-0818 | renew-certs | running | high | `URGENT job-0818: renew-certs -- running` |
| job-0052 | send-digest | pending | low | `DEFERRABLE job-0052: send-digest -- pending` |
| job-0123 | reindex-search | failed | high | `URGENT job-0123: reindex-search -- failed` |
| job-0564 | nightly-backup | running | low | `DEFERRABLE job-0564: nightly-backup -- running` |
| job-0502 | send-digest | pending | high | `URGENT job-0502: send-digest -- pending` |
| job-0689 | purge-cache | running | high | `URGENT job-0689: purge-cache -- running` |
| job-0245 | send-digest | running | high | `URGENT job-0245: send-digest -- running` |
| job-0075 | rotate-keys | done | low | `DEFERRABLE job-0075: rotate-keys -- done` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
