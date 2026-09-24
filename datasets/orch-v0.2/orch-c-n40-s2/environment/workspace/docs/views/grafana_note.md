# Grafana Note view

Module: `views/grafana_note.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0118 | sync-inventory | failed | low | `job-0118 | sync-inventory | failed level=1` |
| job-0314 | reindex-search | failed | low | `job-0314 | reindex-search | failed level=1` |
| job-0071 | reindex-search | done | normal | `job-0071 | reindex-search | done level=2` |
| job-0265 | purge-cache | pending | low | `job-0265 | purge-cache | pending level=1` |
| job-0265 | export-ledger | done | low | `job-0265 | export-ledger | done level=1` |
| job-0611 | invoice-run | done | high | `job-0611 | invoice-run | done level=3` |
| job-0194 | sync-inventory | failed | normal | `job-0194 | sync-inventory | failed level=2` |
| job-0729 | purge-cache | done | high | `job-0729 | purge-cache | done level=3` |
| job-0024 | export-ledger | pending | normal | `job-0024 | export-ledger | pending level=2` |
| job-0748 | renew-certs | done | normal | `job-0748 | renew-certs | done level=2` |
| job-0888 | send-digest | running | high | `job-0888 | send-digest | running level=3` |
| job-0455 | renew-certs | running | normal | `job-0455 | renew-certs | running level=2` |
| job-0279 | sync-inventory | done | high | `job-0279 | sync-inventory | done level=3` |
| job-0411 | rebuild-feed | done | low | `job-0411 | rebuild-feed | done level=1` |

## History

- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
