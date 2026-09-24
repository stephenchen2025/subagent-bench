# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: the on-call engineer who is paged at night.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0645 | reindex-search | pending | low | `level=1 job job-0645 / reindex-search / pending` |
| job-0227 | resize-images | failed | high | `level=3 job job-0227 / resize-images / failed` |
| job-0589 | rebuild-feed | failed | normal | `level=2 job job-0589 / rebuild-feed / failed` |
| job-0146 | renew-certs | done | low | `level=1 job job-0146 / renew-certs / done` |
| job-0047 | compact-logs | running | low | `level=1 job job-0047 / compact-logs / running` |
| job-0874 | sync-inventory | pending | normal | `level=2 job job-0874 / sync-inventory / pending` |
| job-0299 | export-ledger | running | normal | `level=2 job job-0299 / export-ledger / running` |
| job-0098 | rebuild-feed | running | high | `level=3 job job-0098 / rebuild-feed / running` |
| job-0964 | purge-cache | running | low | `level=1 job job-0964 / purge-cache / running` |
| job-0754 | export-ledger | running | normal | `level=2 job job-0754 / export-ledger / running` |
| job-0481 | send-digest | running | low | `level=1 job job-0481 / send-digest / running` |
| job-0504 | purge-cache | failed | low | `level=1 job job-0504 / purge-cache / failed` |
| job-0840 | rebuild-feed | running | high | `level=3 job job-0840 / rebuild-feed / running` |
| job-0779 | send-digest | failed | normal | `level=2 job job-0779 / send-digest / failed` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
