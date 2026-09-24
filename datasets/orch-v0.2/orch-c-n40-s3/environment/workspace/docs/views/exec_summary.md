# Exec Summary view

Module: `views/exec_summary.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0864 | send-digest | done | high | `URGENT send-digest (job-0864) is done` |
| job-0324 | purge-cache | failed | normal | `ROUTINE purge-cache (job-0324) is failed` |
| job-0557 | reindex-search | running | normal | `ROUTINE reindex-search (job-0557) is running` |
| job-0044 | export-ledger | done | low | `DEFERRABLE export-ledger (job-0044) is done` |
| job-0966 | send-digest | running | high | `URGENT send-digest (job-0966) is running` |
| job-0061 | export-ledger | pending | low | `DEFERRABLE export-ledger (job-0061) is pending` |
| job-0410 | invoice-run | pending | normal | `ROUTINE invoice-run (job-0410) is pending` |
| job-0749 | compact-logs | done | high | `URGENT compact-logs (job-0749) is done` |
| job-0959 | send-digest | done | low | `DEFERRABLE send-digest (job-0959) is done` |
| job-0367 | nightly-backup | running | normal | `ROUTINE nightly-backup (job-0367) is running` |
| job-0421 | rebuild-feed | done | normal | `ROUTINE rebuild-feed (job-0421) is done` |
| job-0775 | nightly-backup | pending | high | `URGENT nightly-backup (job-0775) is pending` |
| job-0287 | rebuild-feed | running | high | `URGENT rebuild-feed (job-0287) is running` |
| job-0614 | rotate-keys | pending | low | `DEFERRABLE rotate-keys (job-0614) is pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
