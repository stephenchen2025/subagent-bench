# Tv Wall view

Module: `views/tv_wall.py`. Audience: the on-call engineer who is paged at night.

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
| job-0029 | compact-logs | done | high | `compact-logs (job-0029) is done ^^` |
| job-0690 | sync-inventory | pending | high | `sync-inventory (job-0690) is pending ^^` |
| job-0674 | purge-cache | pending | low | `purge-cache (job-0674) is pending vv` |
| job-0032 | nightly-backup | done | high | `nightly-backup (job-0032) is done ^^` |
| job-0620 | purge-cache | running | low | `purge-cache (job-0620) is running vv` |
| job-0343 | purge-cache | pending | low | `purge-cache (job-0343) is pending vv` |
| job-0240 | export-ledger | running | low | `export-ledger (job-0240) is running vv` |
| job-0841 | invoice-run | failed | low | `invoice-run (job-0841) is failed vv` |
| job-0917 | purge-cache | done | low | `purge-cache (job-0917) is done vv` |
| job-0508 | purge-cache | failed | high | `purge-cache (job-0508) is failed ^^` |
| job-0915 | rebuild-feed | pending | high | `rebuild-feed (job-0915) is pending ^^` |
| job-0844 | nightly-backup | done | high | `nightly-backup (job-0844) is done ^^` |
| job-0341 | renew-certs | failed | normal | `renew-certs (job-0341) is failed --` |
| job-0613 | nightly-backup | done | low | `nightly-backup (job-0613) is done vv` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
