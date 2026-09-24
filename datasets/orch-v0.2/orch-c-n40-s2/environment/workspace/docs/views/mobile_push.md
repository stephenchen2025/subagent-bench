# Mobile Push view

Module: `views/mobile_push.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0539 | rebuild-feed | done | low | `! DONE: rebuild-feed [job-0539]` |
| job-0436 | export-ledger | done | high | `!!! DONE: export-ledger [job-0436]` |
| job-0241 | send-digest | done | high | `!!! DONE: send-digest [job-0241]` |
| job-0703 | renew-certs | pending | high | `!!! PENDING: renew-certs [job-0703]` |
| job-0008 | renew-certs | done | high | `!!! DONE: renew-certs [job-0008]` |
| job-0442 | sync-inventory | failed | normal | `!! FAILED: sync-inventory [job-0442]` |
| job-0980 | rotate-keys | running | low | `! RUNNING: rotate-keys [job-0980]` |
| job-0833 | send-digest | pending | high | `!!! PENDING: send-digest [job-0833]` |
| job-0285 | renew-certs | failed | low | `! FAILED: renew-certs [job-0285]` |
| job-0291 | send-digest | done | normal | `!! DONE: send-digest [job-0291]` |
| job-0323 | resize-images | running | normal | `!! RUNNING: resize-images [job-0323]` |
| job-0765 | nightly-backup | running | high | `!!! RUNNING: nightly-backup [job-0765]` |
| job-0383 | reindex-search | pending | low | `! PENDING: reindex-search [job-0383]` |
| job-0222 | rebuild-feed | running | low | `! RUNNING: rebuild-feed [job-0222]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
