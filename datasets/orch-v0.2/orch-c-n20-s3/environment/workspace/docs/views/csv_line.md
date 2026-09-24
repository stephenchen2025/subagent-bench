# Csv Line view

Module: `views/csv_line.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0533 | reindex-search | failed | normal | `priority:normal FAILED: reindex-search [job-0533]` |
| job-0075 | renew-certs | failed | low | `priority:low FAILED: renew-certs [job-0075]` |
| job-0258 | invoice-run | failed | normal | `priority:normal FAILED: invoice-run [job-0258]` |
| job-0760 | nightly-backup | running | normal | `priority:normal RUNNING: nightly-backup [job-0760]` |
| job-0515 | rebuild-feed | pending | normal | `priority:normal PENDING: rebuild-feed [job-0515]` |
| job-0909 | nightly-backup | running | high | `priority:high RUNNING: nightly-backup [job-0909]` |
| job-0066 | nightly-backup | done | low | `priority:low DONE: nightly-backup [job-0066]` |
| job-0549 | send-digest | pending | high | `priority:high PENDING: send-digest [job-0549]` |
| job-0181 | send-digest | done | normal | `priority:normal DONE: send-digest [job-0181]` |
| job-0425 | reindex-search | failed | normal | `priority:normal FAILED: reindex-search [job-0425]` |
| job-0601 | export-ledger | running | low | `priority:low RUNNING: export-ledger [job-0601]` |
| job-0325 | compact-logs | done | high | `priority:high DONE: compact-logs [job-0325]` |
| job-0275 | sync-inventory | pending | high | `priority:high PENDING: sync-inventory [job-0275]` |
| job-0016 | reindex-search | pending | high | `priority:high PENDING: reindex-search [job-0016]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
