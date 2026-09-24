# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: the on-call engineer who is paged at night.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0334 | rotate-keys | running | normal | `level=2 rotate-keys (job-0334) is running` |
| job-0119 | nightly-backup | running | normal | `level=2 nightly-backup (job-0119) is running` |
| job-0490 | export-ledger | pending | low | `level=1 export-ledger (job-0490) is pending` |
| job-0733 | sync-inventory | done | high | `level=3 sync-inventory (job-0733) is done` |
| job-0920 | send-digest | running | high | `level=3 send-digest (job-0920) is running` |
| job-0891 | rebuild-feed | running | low | `level=1 rebuild-feed (job-0891) is running` |
| job-0486 | reindex-search | pending | high | `level=3 reindex-search (job-0486) is pending` |
| job-0793 | renew-certs | failed | high | `level=3 renew-certs (job-0793) is failed` |
| job-0059 | rotate-keys | running | high | `level=3 rotate-keys (job-0059) is running` |
| job-0619 | renew-certs | running | normal | `level=2 renew-certs (job-0619) is running` |
| job-0925 | purge-cache | pending | normal | `level=2 purge-cache (job-0925) is pending` |
| job-0349 | sync-inventory | failed | normal | `level=2 sync-inventory (job-0349) is failed` |
| job-0089 | invoice-run | failed | normal | `level=2 invoice-run (job-0089) is failed` |
| job-0925 | invoice-run | done | high | `level=3 invoice-run (job-0925) is done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
