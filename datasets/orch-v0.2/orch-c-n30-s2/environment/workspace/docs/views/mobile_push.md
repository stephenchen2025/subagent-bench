# Mobile Push view

Module: `views/mobile_push.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0925 | sync-inventory | pending | normal | `-- sync-inventory (job-0925) is pending` |
| job-0034 | renew-certs | done | high | `^^ renew-certs (job-0034) is done` |
| job-0863 | purge-cache | done | normal | `-- purge-cache (job-0863) is done` |
| job-0696 | reindex-search | done | high | `^^ reindex-search (job-0696) is done` |
| job-0033 | reindex-search | done | low | `vv reindex-search (job-0033) is done` |
| job-0552 | rotate-keys | failed | normal | `-- rotate-keys (job-0552) is failed` |
| job-0817 | invoice-run | pending | high | `^^ invoice-run (job-0817) is pending` |
| job-0064 | rebuild-feed | failed | low | `vv rebuild-feed (job-0064) is failed` |
| job-0863 | purge-cache | pending | high | `^^ purge-cache (job-0863) is pending` |
| job-0497 | compact-logs | failed | low | `vv compact-logs (job-0497) is failed` |
| job-0187 | send-digest | done | normal | `-- send-digest (job-0187) is done` |
| job-0244 | rebuild-feed | pending | low | `vv rebuild-feed (job-0244) is pending` |
| job-0216 | reindex-search | failed | low | `vv reindex-search (job-0216) is failed` |
| job-0650 | reindex-search | running | normal | `-- reindex-search (job-0650) is running` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
