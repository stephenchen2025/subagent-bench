# Jira Comment view

Module: `views/jira_comment.py`. Audience: the platform team's wall display.

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
| job-0602 | renew-certs | failed | high | `FAILED: renew-certs [job-0602] priority:high` |
| job-0831 | reindex-search | pending | low | `PENDING: reindex-search [job-0831] priority:low` |
| job-0482 | rebuild-feed | done | normal | `DONE: rebuild-feed [job-0482] priority:normal` |
| job-0596 | compact-logs | done | normal | `DONE: compact-logs [job-0596] priority:normal` |
| job-0225 | export-ledger | pending | normal | `PENDING: export-ledger [job-0225] priority:normal` |
| job-0298 | resize-images | failed | high | `FAILED: resize-images [job-0298] priority:high` |
| job-0611 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0611] priority:low` |
| job-0465 | send-digest | pending | normal | `PENDING: send-digest [job-0465] priority:normal` |
| job-0926 | purge-cache | done | high | `DONE: purge-cache [job-0926] priority:high` |
| job-0960 | export-ledger | pending | normal | `PENDING: export-ledger [job-0960] priority:normal` |
| job-0270 | reindex-search | running | low | `RUNNING: reindex-search [job-0270] priority:low` |
| job-0508 | rotate-keys | running | normal | `RUNNING: rotate-keys [job-0508] priority:normal` |
| job-0219 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0219] priority:low` |
| job-0649 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0649] priority:low` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
