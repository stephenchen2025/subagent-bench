# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: auditors reviewing job history.

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
| job-0304 | reindex-search | running | high | `priority:high RUNNING: reindex-search [job-0304]` |
| job-0481 | export-ledger | failed | high | `priority:high FAILED: export-ledger [job-0481]` |
| job-0419 | purge-cache | done | low | `priority:low DONE: purge-cache [job-0419]` |
| job-0924 | send-digest | done | normal | `priority:normal DONE: send-digest [job-0924]` |
| job-0029 | reindex-search | failed | low | `priority:low FAILED: reindex-search [job-0029]` |
| job-0814 | sync-inventory | pending | normal | `priority:normal PENDING: sync-inventory [job-0814]` |
| job-0095 | purge-cache | running | high | `priority:high RUNNING: purge-cache [job-0095]` |
| job-0290 | reindex-search | running | normal | `priority:normal RUNNING: reindex-search [job-0290]` |
| job-0059 | sync-inventory | failed | normal | `priority:normal FAILED: sync-inventory [job-0059]` |
| job-0506 | sync-inventory | done | high | `priority:high DONE: sync-inventory [job-0506]` |
| job-0194 | send-digest | done | low | `priority:low DONE: send-digest [job-0194]` |
| job-0936 | purge-cache | failed | low | `priority:low FAILED: purge-cache [job-0936]` |
| job-0103 | send-digest | done | high | `priority:high DONE: send-digest [job-0103]` |
| job-0710 | rebuild-feed | running | high | `priority:high RUNNING: rebuild-feed [job-0710]` |

## History

- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
