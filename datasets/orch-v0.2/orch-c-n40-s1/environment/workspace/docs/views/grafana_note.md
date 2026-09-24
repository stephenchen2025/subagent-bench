# Grafana Note view

Module: `views/grafana_note.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0331 | send-digest | failed | normal | `P2 send-digest (job-0331) is failed` |
| job-0144 | rebuild-feed | pending | low | `P3 rebuild-feed (job-0144) is pending` |
| job-0179 | rotate-keys | running | high | `P1 rotate-keys (job-0179) is running` |
| job-0286 | sync-inventory | done | high | `P1 sync-inventory (job-0286) is done` |
| job-0567 | purge-cache | done | low | `P3 purge-cache (job-0567) is done` |
| job-0046 | nightly-backup | failed | normal | `P2 nightly-backup (job-0046) is failed` |
| job-0152 | send-digest | done | normal | `P2 send-digest (job-0152) is done` |
| job-0364 | invoice-run | done | high | `P1 invoice-run (job-0364) is done` |
| job-0202 | renew-certs | failed | normal | `P2 renew-certs (job-0202) is failed` |
| job-0558 | nightly-backup | failed | normal | `P2 nightly-backup (job-0558) is failed` |
| job-0857 | renew-certs | failed | high | `P1 renew-certs (job-0857) is failed` |
| job-0047 | reindex-search | running | normal | `P2 reindex-search (job-0047) is running` |
| job-0968 | rotate-keys | done | normal | `P2 rotate-keys (job-0968) is done` |
| job-0339 | renew-certs | running | low | `P3 renew-certs (job-0339) is running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
