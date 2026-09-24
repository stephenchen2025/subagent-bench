# Grafana Note view

Module: `views/grafana_note.py`. Audience: auditors reviewing job history.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0316 | nightly-backup | done | high | `color=red job-0316 | nightly-backup | done` |
| job-0572 | export-ledger | pending | high | `color=red job-0572 | export-ledger | pending` |
| job-0228 | export-ledger | failed | normal | `color=amber job-0228 | export-ledger | failed` |
| job-0512 | export-ledger | running | low | `color=green job-0512 | export-ledger | running` |
| job-0923 | compact-logs | running | low | `color=green job-0923 | compact-logs | running` |
| job-0299 | nightly-backup | running | high | `color=red job-0299 | nightly-backup | running` |
| job-0279 | purge-cache | failed | normal | `color=amber job-0279 | purge-cache | failed` |
| job-0284 | compact-logs | running | normal | `color=amber job-0284 | compact-logs | running` |
| job-0829 | nightly-backup | done | high | `color=red job-0829 | nightly-backup | done` |
| job-0382 | invoice-run | pending | normal | `color=amber job-0382 | invoice-run | pending` |
| job-0472 | export-ledger | done | high | `color=red job-0472 | export-ledger | done` |
| job-0933 | rebuild-feed | failed | normal | `color=amber job-0933 | rebuild-feed | failed` |
| job-0410 | purge-cache | running | high | `color=red job-0410 | purge-cache | running` |
| job-0144 | invoice-run | failed | low | `color=green job-0144 | invoice-run | failed` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
