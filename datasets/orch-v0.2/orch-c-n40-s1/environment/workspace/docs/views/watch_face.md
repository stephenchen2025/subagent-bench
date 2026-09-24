# Watch Face view

Module: `views/watch_face.py`. Audience: release managers.

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
| job-0083 | nightly-backup | running | normal | `priority:normal RUNNING: nightly-backup [job-0083]` |
| job-0655 | resize-images | running | normal | `priority:normal RUNNING: resize-images [job-0655]` |
| job-0797 | reindex-search | done | normal | `priority:normal DONE: reindex-search [job-0797]` |
| job-0502 | rebuild-feed | done | high | `priority:high DONE: rebuild-feed [job-0502]` |
| job-0755 | compact-logs | done | low | `priority:low DONE: compact-logs [job-0755]` |
| job-0723 | sync-inventory | pending | high | `priority:high PENDING: sync-inventory [job-0723]` |
| job-0923 | export-ledger | done | low | `priority:low DONE: export-ledger [job-0923]` |
| job-0381 | compact-logs | pending | normal | `priority:normal PENDING: compact-logs [job-0381]` |
| job-0123 | resize-images | running | normal | `priority:normal RUNNING: resize-images [job-0123]` |
| job-0264 | renew-certs | done | low | `priority:low DONE: renew-certs [job-0264]` |
| job-0925 | send-digest | running | low | `priority:low RUNNING: send-digest [job-0925]` |
| job-0223 | compact-logs | done | high | `priority:high DONE: compact-logs [job-0223]` |
| job-0076 | purge-cache | done | low | `priority:low DONE: purge-cache [job-0076]` |
| job-0598 | reindex-search | done | normal | `priority:normal DONE: reindex-search [job-0598]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
