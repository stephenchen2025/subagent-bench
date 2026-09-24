# Teams Card view

Module: `views/teams_card.py`. Audience: the executive summary email.

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
| job-0894 | compact-logs | done | low | `priority:low DONE: compact-logs [job-0894]` |
| job-0114 | rebuild-feed | failed | normal | `priority:normal FAILED: rebuild-feed [job-0114]` |
| job-0012 | purge-cache | done | normal | `priority:normal DONE: purge-cache [job-0012]` |
| job-0248 | rebuild-feed | failed | normal | `priority:normal FAILED: rebuild-feed [job-0248]` |
| job-0458 | send-digest | failed | high | `priority:high FAILED: send-digest [job-0458]` |
| job-0290 | sync-inventory | failed | normal | `priority:normal FAILED: sync-inventory [job-0290]` |
| job-0184 | invoice-run | failed | high | `priority:high FAILED: invoice-run [job-0184]` |
| job-0812 | rebuild-feed | running | low | `priority:low RUNNING: rebuild-feed [job-0812]` |
| job-0720 | rebuild-feed | running | low | `priority:low RUNNING: rebuild-feed [job-0720]` |
| job-0219 | compact-logs | running | normal | `priority:normal RUNNING: compact-logs [job-0219]` |
| job-0023 | compact-logs | pending | normal | `priority:normal PENDING: compact-logs [job-0023]` |
| job-0352 | rebuild-feed | pending | high | `priority:high PENDING: rebuild-feed [job-0352]` |
| job-0533 | nightly-backup | running | high | `priority:high RUNNING: nightly-backup [job-0533]` |
| job-0053 | sync-inventory | pending | high | `priority:high PENDING: sync-inventory [job-0053]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
