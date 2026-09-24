# Calendar Note view

Module: `views/calendar_note.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0870 | reindex-search | pending | low | `PENDING: reindex-search [job-0870] priority:low` |
| job-0096 | compact-logs | failed | high | `FAILED: compact-logs [job-0096] priority:high` |
| job-0879 | compact-logs | failed | high | `FAILED: compact-logs [job-0879] priority:high` |
| job-0410 | nightly-backup | failed | high | `FAILED: nightly-backup [job-0410] priority:high` |
| job-0398 | rebuild-feed | pending | normal | `PENDING: rebuild-feed [job-0398] priority:normal` |
| job-0050 | send-digest | done | normal | `DONE: send-digest [job-0050] priority:normal` |
| job-0412 | resize-images | failed | low | `FAILED: resize-images [job-0412] priority:low` |
| job-0137 | rotate-keys | done | normal | `DONE: rotate-keys [job-0137] priority:normal` |
| job-0720 | export-ledger | pending | normal | `PENDING: export-ledger [job-0720] priority:normal` |
| job-0379 | resize-images | running | high | `RUNNING: resize-images [job-0379] priority:high` |
| job-0520 | nightly-backup | running | low | `RUNNING: nightly-backup [job-0520] priority:low` |
| job-0295 | compact-logs | failed | high | `FAILED: compact-logs [job-0295] priority:high` |
| job-0675 | resize-images | running | normal | `RUNNING: resize-images [job-0675] priority:normal` |
| job-0013 | export-ledger | failed | high | `FAILED: export-ledger [job-0013] priority:high` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
