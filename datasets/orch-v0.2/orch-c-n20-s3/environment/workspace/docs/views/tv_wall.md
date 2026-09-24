# Tv Wall view

Module: `views/tv_wall.py`. Audience: the finance team's weekly review.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0417 | invoice-run | failed | low | `vv FAILED: invoice-run [job-0417]` |
| job-0641 | invoice-run | running | low | `vv RUNNING: invoice-run [job-0641]` |
| job-0862 | nightly-backup | failed | high | `^^ FAILED: nightly-backup [job-0862]` |
| job-0498 | reindex-search | failed | normal | `-- FAILED: reindex-search [job-0498]` |
| job-0576 | sync-inventory | failed | low | `vv FAILED: sync-inventory [job-0576]` |
| job-0711 | reindex-search | failed | high | `^^ FAILED: reindex-search [job-0711]` |
| job-0899 | send-digest | failed | high | `^^ FAILED: send-digest [job-0899]` |
| job-0974 | resize-images | failed | low | `vv FAILED: resize-images [job-0974]` |
| job-0404 | resize-images | running | low | `vv RUNNING: resize-images [job-0404]` |
| job-0292 | sync-inventory | done | low | `vv DONE: sync-inventory [job-0292]` |
| job-0118 | rebuild-feed | pending | high | `^^ PENDING: rebuild-feed [job-0118]` |
| job-0582 | export-ledger | pending | normal | `-- PENDING: export-ledger [job-0582]` |
| job-0237 | resize-images | running | normal | `-- RUNNING: resize-images [job-0237]` |
| job-0938 | purge-cache | pending | high | `^^ PENDING: purge-cache [job-0938]` |

## History

- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
