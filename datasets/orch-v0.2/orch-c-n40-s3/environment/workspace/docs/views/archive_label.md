# Archive Label view

Module: `views/archive_label.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0107 | nightly-backup | failed | low | `FAILED: nightly-backup [job-0107] level=1` |
| job-0037 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0037] level=1` |
| job-0056 | resize-images | failed | low | `FAILED: resize-images [job-0056] level=1` |
| job-0522 | export-ledger | done | low | `DONE: export-ledger [job-0522] level=1` |
| job-0633 | reindex-search | failed | low | `FAILED: reindex-search [job-0633] level=1` |
| job-0174 | send-digest | pending | normal | `PENDING: send-digest [job-0174] level=2` |
| job-0177 | nightly-backup | failed | high | `FAILED: nightly-backup [job-0177] level=3` |
| job-0862 | export-ledger | failed | low | `FAILED: export-ledger [job-0862] level=1` |
| job-0235 | compact-logs | pending | low | `PENDING: compact-logs [job-0235] level=1` |
| job-0488 | compact-logs | pending | normal | `PENDING: compact-logs [job-0488] level=2` |
| job-0384 | compact-logs | done | low | `DONE: compact-logs [job-0384] level=1` |
| job-0410 | sync-inventory | done | high | `DONE: sync-inventory [job-0410] level=3` |
| job-0239 | rotate-keys | done | low | `DONE: rotate-keys [job-0239] level=1` |
| job-0360 | compact-logs | failed | low | `FAILED: compact-logs [job-0360] level=1` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
