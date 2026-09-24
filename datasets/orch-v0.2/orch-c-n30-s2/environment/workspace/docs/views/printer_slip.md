# Printer Slip view

Module: `views/printer_slip.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0683 | invoice-run | running | normal | `invoice-run (job-0683) is running **` |
| job-0154 | sync-inventory | pending | high | `sync-inventory (job-0154) is pending ***` |
| job-0741 | send-digest | running | normal | `send-digest (job-0741) is running **` |
| job-0815 | invoice-run | running | low | `invoice-run (job-0815) is running *` |
| job-0384 | sync-inventory | pending | normal | `sync-inventory (job-0384) is pending **` |
| job-0950 | invoice-run | running | low | `invoice-run (job-0950) is running *` |
| job-0830 | purge-cache | running | high | `purge-cache (job-0830) is running ***` |
| job-0759 | sync-inventory | failed | low | `sync-inventory (job-0759) is failed *` |
| job-0279 | export-ledger | failed | normal | `export-ledger (job-0279) is failed **` |
| job-0508 | nightly-backup | running | normal | `nightly-backup (job-0508) is running **` |
| job-0910 | reindex-search | failed | low | `reindex-search (job-0910) is failed *` |
| job-0731 | renew-certs | running | normal | `renew-certs (job-0731) is running **` |
| job-0508 | send-digest | running | normal | `send-digest (job-0508) is running **` |
| job-0222 | rotate-keys | running | high | `rotate-keys (job-0222) is running ***` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
