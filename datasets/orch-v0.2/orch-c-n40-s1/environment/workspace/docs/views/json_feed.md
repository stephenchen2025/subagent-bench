# Json Feed view

Module: `views/json_feed.py`. Audience: the executive summary email.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0875 | send-digest | done | normal | `send-digest (job-0875) is done priority:normal` |
| job-0813 | sync-inventory | failed | normal | `sync-inventory (job-0813) is failed priority:normal` |
| job-0396 | export-ledger | running | low | `export-ledger (job-0396) is running priority:low` |
| job-0776 | sync-inventory | pending | low | `sync-inventory (job-0776) is pending priority:low` |
| job-0481 | rebuild-feed | pending | high | `rebuild-feed (job-0481) is pending priority:high` |
| job-0208 | reindex-search | done | low | `reindex-search (job-0208) is done priority:low` |
| job-0596 | send-digest | pending | normal | `send-digest (job-0596) is pending priority:normal` |
| job-0415 | sync-inventory | failed | normal | `sync-inventory (job-0415) is failed priority:normal` |
| job-0007 | purge-cache | pending | low | `purge-cache (job-0007) is pending priority:low` |
| job-0384 | invoice-run | failed | low | `invoice-run (job-0384) is failed priority:low` |
| job-0011 | invoice-run | running | normal | `invoice-run (job-0011) is running priority:normal` |
| job-0376 | export-ledger | done | normal | `export-ledger (job-0376) is done priority:normal` |
| job-0356 | purge-cache | failed | low | `purge-cache (job-0356) is failed priority:low` |
| job-0003 | renew-certs | failed | high | `renew-certs (job-0003) is failed priority:high` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
