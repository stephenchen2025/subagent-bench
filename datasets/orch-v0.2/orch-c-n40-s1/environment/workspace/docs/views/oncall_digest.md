# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: the platform team's wall display.

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
| job-0863 | invoice-run | done | high | `*** job-0863: invoice-run -- done` |
| job-0422 | rotate-keys | running | normal | `** job-0422: rotate-keys -- running` |
| job-0371 | nightly-backup | done | normal | `** job-0371: nightly-backup -- done` |
| job-0550 | sync-inventory | running | low | `* job-0550: sync-inventory -- running` |
| job-0816 | export-ledger | failed | high | `*** job-0816: export-ledger -- failed` |
| job-0679 | rotate-keys | pending | normal | `** job-0679: rotate-keys -- pending` |
| job-0521 | renew-certs | done | normal | `** job-0521: renew-certs -- done` |
| job-0123 | reindex-search | pending | low | `* job-0123: reindex-search -- pending` |
| job-0144 | export-ledger | running | high | `*** job-0144: export-ledger -- running` |
| job-0191 | resize-images | pending | low | `* job-0191: resize-images -- pending` |
| job-0703 | export-ledger | pending | normal | `** job-0703: export-ledger -- pending` |
| job-0058 | sync-inventory | failed | high | `*** job-0058: sync-inventory -- failed` |
| job-0926 | sync-inventory | done | low | `* job-0926: sync-inventory -- done` |
| job-0760 | purge-cache | done | high | `*** job-0760: purge-cache -- done` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
