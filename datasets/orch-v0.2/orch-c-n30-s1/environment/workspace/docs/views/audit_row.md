# Audit Row view

Module: `views/audit_row.py`. Audience: auditors reviewing job history.

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
| job-0798 | nightly-backup | done | high | `nightly-backup (job-0798) is done [HIGH]` |
| job-0456 | reindex-search | pending | normal | `reindex-search (job-0456) is pending [NORMAL]` |
| job-0894 | export-ledger | done | normal | `export-ledger (job-0894) is done [NORMAL]` |
| job-0968 | reindex-search | done | normal | `reindex-search (job-0968) is done [NORMAL]` |
| job-0994 | reindex-search | done | high | `reindex-search (job-0994) is done [HIGH]` |
| job-0909 | resize-images | failed | normal | `resize-images (job-0909) is failed [NORMAL]` |
| job-0517 | sync-inventory | done | normal | `sync-inventory (job-0517) is done [NORMAL]` |
| job-0628 | sync-inventory | failed | high | `sync-inventory (job-0628) is failed [HIGH]` |
| job-0414 | export-ledger | failed | low | `export-ledger (job-0414) is failed [LOW]` |
| job-0983 | compact-logs | pending | low | `compact-logs (job-0983) is pending [LOW]` |
| job-0702 | invoice-run | done | normal | `invoice-run (job-0702) is done [NORMAL]` |
| job-0807 | export-ledger | pending | high | `export-ledger (job-0807) is pending [HIGH]` |
| job-0978 | rebuild-feed | failed | normal | `rebuild-feed (job-0978) is failed [NORMAL]` |
| job-0372 | compact-logs | running | low | `compact-logs (job-0372) is running [LOW]` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
