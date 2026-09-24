# Grafana Note view

Module: `views/grafana_note.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0007 | sync-inventory | done | low | `job job-0007 / sync-inventory / done color=green` |
| job-0510 | purge-cache | failed | high | `job job-0510 / purge-cache / failed color=red` |
| job-0615 | purge-cache | pending | low | `job job-0615 / purge-cache / pending color=green` |
| job-0308 | renew-certs | failed | low | `job job-0308 / renew-certs / failed color=green` |
| job-0718 | reindex-search | pending | normal | `job job-0718 / reindex-search / pending color=amber` |
| job-0591 | reindex-search | running | normal | `job job-0591 / reindex-search / running color=amber` |
| job-0204 | export-ledger | pending | low | `job job-0204 / export-ledger / pending color=green` |
| job-0156 | reindex-search | done | high | `job job-0156 / reindex-search / done color=red` |
| job-0556 | renew-certs | done | normal | `job job-0556 / renew-certs / done color=amber` |
| job-0262 | nightly-backup | pending | low | `job job-0262 / nightly-backup / pending color=green` |
| job-0941 | export-ledger | pending | low | `job job-0941 / export-ledger / pending color=green` |
| job-0954 | reindex-search | failed | high | `job job-0954 / reindex-search / failed color=red` |
| job-0755 | export-ledger | running | normal | `job job-0755 / export-ledger / running color=amber` |
| job-0255 | reindex-search | pending | normal | `job job-0255 / reindex-search / pending color=amber` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
