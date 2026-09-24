# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0330 | purge-cache | failed | normal | `purge-cache (job-0330) is failed [NORMAL]` |
| job-0149 | resize-images | done | low | `resize-images (job-0149) is done [LOW]` |
| job-0403 | invoice-run | done | high | `invoice-run (job-0403) is done [HIGH]` |
| job-0182 | export-ledger | done | normal | `export-ledger (job-0182) is done [NORMAL]` |
| job-0639 | sync-inventory | done | high | `sync-inventory (job-0639) is done [HIGH]` |
| job-0936 | sync-inventory | pending | high | `sync-inventory (job-0936) is pending [HIGH]` |
| job-0686 | rotate-keys | running | high | `rotate-keys (job-0686) is running [HIGH]` |
| job-0733 | renew-certs | failed | high | `renew-certs (job-0733) is failed [HIGH]` |
| job-0878 | reindex-search | failed | normal | `reindex-search (job-0878) is failed [NORMAL]` |
| job-0486 | resize-images | failed | normal | `resize-images (job-0486) is failed [NORMAL]` |
| job-0340 | rebuild-feed | running | high | `rebuild-feed (job-0340) is running [HIGH]` |
| job-0549 | rotate-keys | done | high | `rotate-keys (job-0549) is done [HIGH]` |
| job-0807 | rotate-keys | failed | high | `rotate-keys (job-0807) is failed [HIGH]` |
| job-0112 | compact-logs | done | normal | `compact-logs (job-0112) is done [NORMAL]` |

## History

- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
