# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0541 | invoice-run | failed | low | `DEFERRABLE job-0541 | invoice-run | failed` |
| job-0205 | sync-inventory | pending | high | `URGENT job-0205 | sync-inventory | pending` |
| job-0446 | send-digest | done | high | `URGENT job-0446 | send-digest | done` |
| job-0568 | nightly-backup | pending | low | `DEFERRABLE job-0568 | nightly-backup | pending` |
| job-0228 | export-ledger | running | normal | `ROUTINE job-0228 | export-ledger | running` |
| job-0001 | rotate-keys | running | low | `DEFERRABLE job-0001 | rotate-keys | running` |
| job-0345 | invoice-run | running | normal | `ROUTINE job-0345 | invoice-run | running` |
| job-0482 | export-ledger | failed | high | `URGENT job-0482 | export-ledger | failed` |
| job-0560 | renew-certs | pending | normal | `ROUTINE job-0560 | renew-certs | pending` |
| job-0492 | renew-certs | pending | high | `URGENT job-0492 | renew-certs | pending` |
| job-0936 | renew-certs | pending | normal | `ROUTINE job-0936 | renew-certs | pending` |
| job-0744 | compact-logs | done | normal | `ROUTINE job-0744 | compact-logs | done` |
| job-0615 | resize-images | pending | low | `DEFERRABLE job-0615 | resize-images | pending` |
| job-0120 | rotate-keys | pending | normal | `ROUTINE job-0120 | rotate-keys | pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
