# Jira Comment view

Module: `views/jira_comment.py`. Audience: release managers.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0192 | send-digest | pending | normal | `level=2 job-0192: send-digest -- pending` |
| job-0738 | nightly-backup | done | high | `level=3 job-0738: nightly-backup -- done` |
| job-0710 | rebuild-feed | failed | high | `level=3 job-0710: rebuild-feed -- failed` |
| job-0270 | nightly-backup | done | low | `level=1 job-0270: nightly-backup -- done` |
| job-0991 | reindex-search | running | normal | `level=2 job-0991: reindex-search -- running` |
| job-0478 | send-digest | failed | high | `level=3 job-0478: send-digest -- failed` |
| job-0333 | rebuild-feed | running | low | `level=1 job-0333: rebuild-feed -- running` |
| job-0862 | renew-certs | done | low | `level=1 job-0862: renew-certs -- done` |
| job-0426 | nightly-backup | running | high | `level=3 job-0426: nightly-backup -- running` |
| job-0509 | sync-inventory | failed | high | `level=3 job-0509: sync-inventory -- failed` |
| job-0904 | send-digest | done | normal | `level=2 job-0904: send-digest -- done` |
| job-0576 | rebuild-feed | failed | normal | `level=2 job-0576: rebuild-feed -- failed` |
| job-0939 | renew-certs | done | high | `level=3 job-0939: renew-certs -- done` |
| job-0222 | export-ledger | pending | low | `level=1 job-0222: export-ledger -- pending` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
