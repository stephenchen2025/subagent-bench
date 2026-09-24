# Pager Line view

Module: `views/pager_line.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0433 | purge-cache | failed | high | `purge-cache (job-0433) is failed P1` |
| job-0690 | compact-logs | failed | low | `compact-logs (job-0690) is failed P3` |
| job-0630 | rotate-keys | failed | low | `rotate-keys (job-0630) is failed P3` |
| job-0643 | invoice-run | running | low | `invoice-run (job-0643) is running P3` |
| job-0426 | send-digest | running | normal | `send-digest (job-0426) is running P2` |
| job-0403 | export-ledger | done | low | `export-ledger (job-0403) is done P3` |
| job-0700 | send-digest | failed | normal | `send-digest (job-0700) is failed P2` |
| job-0935 | nightly-backup | failed | normal | `nightly-backup (job-0935) is failed P2` |
| job-0713 | send-digest | pending | high | `send-digest (job-0713) is pending P1` |
| job-0333 | renew-certs | failed | normal | `renew-certs (job-0333) is failed P2` |
| job-0505 | invoice-run | pending | high | `invoice-run (job-0505) is pending P1` |
| job-0496 | export-ledger | running | low | `export-ledger (job-0496) is running P3` |
| job-0116 | rebuild-feed | pending | low | `rebuild-feed (job-0116) is pending P3` |
| job-0300 | invoice-run | done | low | `invoice-run (job-0300) is done P3` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
