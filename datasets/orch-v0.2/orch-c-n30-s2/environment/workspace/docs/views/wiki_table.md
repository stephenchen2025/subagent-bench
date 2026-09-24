# Wiki Table view

Module: `views/wiki_table.py`. Audience: customer support leads.

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
| job-0663 | send-digest | pending | low | `send-digest (job-0663) is pending [LOW]` |
| job-0853 | rotate-keys | pending | low | `rotate-keys (job-0853) is pending [LOW]` |
| job-0397 | rotate-keys | failed | normal | `rotate-keys (job-0397) is failed [NORMAL]` |
| job-0386 | rotate-keys | failed | low | `rotate-keys (job-0386) is failed [LOW]` |
| job-0310 | renew-certs | done | high | `renew-certs (job-0310) is done [HIGH]` |
| job-0105 | compact-logs | running | normal | `compact-logs (job-0105) is running [NORMAL]` |
| job-0848 | export-ledger | failed | low | `export-ledger (job-0848) is failed [LOW]` |
| job-0473 | send-digest | pending | normal | `send-digest (job-0473) is pending [NORMAL]` |
| job-0032 | purge-cache | done | high | `purge-cache (job-0032) is done [HIGH]` |
| job-0977 | invoice-run | done | normal | `invoice-run (job-0977) is done [NORMAL]` |
| job-0740 | purge-cache | running | low | `purge-cache (job-0740) is running [LOW]` |
| job-0112 | sync-inventory | running | low | `sync-inventory (job-0112) is running [LOW]` |
| job-0436 | renew-certs | done | high | `renew-certs (job-0436) is done [HIGH]` |
| job-0694 | rotate-keys | running | normal | `rotate-keys (job-0694) is running [NORMAL]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
