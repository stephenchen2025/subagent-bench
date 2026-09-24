# Watch Face view

Module: `views/watch_face.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0024 | rebuild-feed | running | high | `rebuild-feed (job-0024) is running ^^` |
| job-0413 | purge-cache | pending | normal | `purge-cache (job-0413) is pending --` |
| job-0748 | invoice-run | running | low | `invoice-run (job-0748) is running vv` |
| job-0840 | send-digest | running | high | `send-digest (job-0840) is running ^^` |
| job-0694 | reindex-search | done | high | `reindex-search (job-0694) is done ^^` |
| job-0542 | purge-cache | running | high | `purge-cache (job-0542) is running ^^` |
| job-0118 | renew-certs | done | normal | `renew-certs (job-0118) is done --` |
| job-0321 | rebuild-feed | failed | normal | `rebuild-feed (job-0321) is failed --` |
| job-0761 | reindex-search | failed | normal | `reindex-search (job-0761) is failed --` |
| job-0805 | export-ledger | failed | normal | `export-ledger (job-0805) is failed --` |
| job-0522 | renew-certs | failed | low | `renew-certs (job-0522) is failed vv` |
| job-0726 | compact-logs | done | normal | `compact-logs (job-0726) is done --` |
| job-0703 | renew-certs | pending | normal | `renew-certs (job-0703) is pending --` |
| job-0324 | sync-inventory | pending | low | `sync-inventory (job-0324) is pending vv` |

## History

- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
