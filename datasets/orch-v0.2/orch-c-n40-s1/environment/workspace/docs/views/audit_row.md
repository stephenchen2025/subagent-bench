# Audit Row view

Module: `views/audit_row.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0205 | rebuild-feed | pending | low | `PENDING: rebuild-feed [job-0205] P3` |
| job-0847 | rebuild-feed | failed | low | `FAILED: rebuild-feed [job-0847] P3` |
| job-0849 | export-ledger | done | low | `DONE: export-ledger [job-0849] P3` |
| job-0562 | compact-logs | failed | normal | `FAILED: compact-logs [job-0562] P2` |
| job-0011 | resize-images | pending | high | `PENDING: resize-images [job-0011] P1` |
| job-0799 | invoice-run | done | high | `DONE: invoice-run [job-0799] P1` |
| job-0965 | send-digest | running | low | `RUNNING: send-digest [job-0965] P3` |
| job-0460 | rebuild-feed | pending | high | `PENDING: rebuild-feed [job-0460] P1` |
| job-0065 | export-ledger | running | normal | `RUNNING: export-ledger [job-0065] P2` |
| job-0833 | reindex-search | running | low | `RUNNING: reindex-search [job-0833] P3` |
| job-0577 | reindex-search | running | normal | `RUNNING: reindex-search [job-0577] P2` |
| job-0988 | sync-inventory | pending | low | `PENDING: sync-inventory [job-0988] P3` |
| job-0125 | reindex-search | done | high | `DONE: reindex-search [job-0125] P1` |
| job-0892 | resize-images | done | normal | `DONE: resize-images [job-0892] P2` |

## History

- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
