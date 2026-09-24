# Sla Board view

Module: `views/sla_board.py`. Audience: the finance team's weekly review.

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
| job-0285 | invoice-run | pending | low | `invoice-run (job-0285) is pending vv` |
| job-0099 | rotate-keys | failed | high | `rotate-keys (job-0099) is failed ^^` |
| job-0961 | invoice-run | pending | high | `invoice-run (job-0961) is pending ^^` |
| job-0767 | rebuild-feed | failed | high | `rebuild-feed (job-0767) is failed ^^` |
| job-0952 | renew-certs | done | low | `renew-certs (job-0952) is done vv` |
| job-0608 | export-ledger | pending | normal | `export-ledger (job-0608) is pending --` |
| job-0655 | rotate-keys | done | low | `rotate-keys (job-0655) is done vv` |
| job-0172 | send-digest | running | high | `send-digest (job-0172) is running ^^` |
| job-0927 | resize-images | pending | low | `resize-images (job-0927) is pending vv` |
| job-0150 | nightly-backup | pending | low | `nightly-backup (job-0150) is pending vv` |
| job-0493 | export-ledger | done | high | `export-ledger (job-0493) is done ^^` |
| job-0463 | reindex-search | running | normal | `reindex-search (job-0463) is running --` |
| job-0571 | nightly-backup | done | normal | `nightly-backup (job-0571) is done --` |
| job-0616 | reindex-search | failed | normal | `reindex-search (job-0616) is failed --` |

## History

- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
