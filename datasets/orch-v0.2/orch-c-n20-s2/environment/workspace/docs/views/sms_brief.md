# Sms Brief view

Module: `views/sms_brief.py`. Audience: the finance team's weekly review.

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
| job-0396 | export-ledger | running | low | `priority:low RUNNING: export-ledger [job-0396]` |
| job-0685 | reindex-search | pending | low | `priority:low PENDING: reindex-search [job-0685]` |
| job-0071 | invoice-run | pending | high | `priority:high PENDING: invoice-run [job-0071]` |
| job-0279 | rotate-keys | done | high | `priority:high DONE: rotate-keys [job-0279]` |
| job-0435 | renew-certs | failed | normal | `priority:normal FAILED: renew-certs [job-0435]` |
| job-0700 | compact-logs | failed | low | `priority:low FAILED: compact-logs [job-0700]` |
| job-0904 | send-digest | done | normal | `priority:normal DONE: send-digest [job-0904]` |
| job-0536 | send-digest | pending | high | `priority:high PENDING: send-digest [job-0536]` |
| job-0069 | reindex-search | running | high | `priority:high RUNNING: reindex-search [job-0069]` |
| job-0856 | export-ledger | done | normal | `priority:normal DONE: export-ledger [job-0856]` |
| job-0731 | sync-inventory | failed | high | `priority:high FAILED: sync-inventory [job-0731]` |
| job-0329 | rebuild-feed | done | normal | `priority:normal DONE: rebuild-feed [job-0329]` |
| job-0684 | rebuild-feed | running | normal | `priority:normal RUNNING: rebuild-feed [job-0684]` |
| job-0101 | renew-certs | failed | normal | `priority:normal FAILED: renew-certs [job-0101]` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
