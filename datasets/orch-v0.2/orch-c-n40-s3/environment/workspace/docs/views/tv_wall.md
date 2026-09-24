# Tv Wall view

Module: `views/tv_wall.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0101 | reindex-search | failed | normal | `job job-0101 / reindex-search / failed **` |
| job-0758 | renew-certs | pending | low | `job job-0758 / renew-certs / pending *` |
| job-0094 | export-ledger | failed | high | `job job-0094 / export-ledger / failed ***` |
| job-0896 | sync-inventory | done | high | `job job-0896 / sync-inventory / done ***` |
| job-0644 | send-digest | done | low | `job job-0644 / send-digest / done *` |
| job-0824 | send-digest | done | normal | `job job-0824 / send-digest / done **` |
| job-0273 | nightly-backup | running | low | `job job-0273 / nightly-backup / running *` |
| job-0226 | rotate-keys | done | low | `job job-0226 / rotate-keys / done *` |
| job-0583 | export-ledger | done | normal | `job job-0583 / export-ledger / done **` |
| job-0360 | send-digest | running | low | `job job-0360 / send-digest / running *` |
| job-0540 | nightly-backup | running | normal | `job job-0540 / nightly-backup / running **` |
| job-0831 | rotate-keys | failed | high | `job job-0831 / rotate-keys / failed ***` |
| job-0389 | send-digest | pending | normal | `job job-0389 / send-digest / pending **` |
| job-0576 | export-ledger | done | normal | `job job-0576 / export-ledger / done **` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
