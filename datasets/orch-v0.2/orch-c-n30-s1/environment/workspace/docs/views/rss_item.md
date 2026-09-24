# Rss Item view

Module: `views/rss_item.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0947 | rotate-keys | running | low | `DEFERRABLE RUNNING: rotate-keys [job-0947]` |
| job-0044 | invoice-run | done | high | `URGENT DONE: invoice-run [job-0044]` |
| job-0556 | sync-inventory | done | high | `URGENT DONE: sync-inventory [job-0556]` |
| job-0009 | renew-certs | done | low | `DEFERRABLE DONE: renew-certs [job-0009]` |
| job-0816 | reindex-search | running | high | `URGENT RUNNING: reindex-search [job-0816]` |
| job-0173 | export-ledger | pending | normal | `ROUTINE PENDING: export-ledger [job-0173]` |
| job-0143 | export-ledger | failed | normal | `ROUTINE FAILED: export-ledger [job-0143]` |
| job-0432 | nightly-backup | pending | high | `URGENT PENDING: nightly-backup [job-0432]` |
| job-0933 | compact-logs | running | high | `URGENT RUNNING: compact-logs [job-0933]` |
| job-0299 | reindex-search | pending | normal | `ROUTINE PENDING: reindex-search [job-0299]` |
| job-0845 | compact-logs | done | high | `URGENT DONE: compact-logs [job-0845]` |
| job-0629 | rotate-keys | failed | high | `URGENT FAILED: rotate-keys [job-0629]` |
| job-0891 | renew-certs | pending | low | `DEFERRABLE PENDING: renew-certs [job-0891]` |
| job-0737 | renew-certs | failed | normal | `ROUTINE FAILED: renew-certs [job-0737]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
