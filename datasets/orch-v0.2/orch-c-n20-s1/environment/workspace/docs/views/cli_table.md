# Cli Table view

Module: `views/cli_table.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0719 | sync-inventory | failed | high | `level=3 sync-inventory (job-0719) is failed` |
| job-0182 | renew-certs | done | high | `level=3 renew-certs (job-0182) is done` |
| job-0398 | renew-certs | running | low | `level=1 renew-certs (job-0398) is running` |
| job-0588 | rotate-keys | running | low | `level=1 rotate-keys (job-0588) is running` |
| job-0449 | compact-logs | failed | normal | `level=2 compact-logs (job-0449) is failed` |
| job-0740 | resize-images | pending | low | `level=1 resize-images (job-0740) is pending` |
| job-0701 | export-ledger | running | high | `level=3 export-ledger (job-0701) is running` |
| job-0620 | renew-certs | running | high | `level=3 renew-certs (job-0620) is running` |
| job-0038 | compact-logs | pending | normal | `level=2 compact-logs (job-0038) is pending` |
| job-0151 | nightly-backup | failed | high | `level=3 nightly-backup (job-0151) is failed` |
| job-0894 | reindex-search | failed | normal | `level=2 reindex-search (job-0894) is failed` |
| job-0091 | nightly-backup | running | high | `level=3 nightly-backup (job-0091) is running` |
| job-0726 | compact-logs | failed | normal | `level=2 compact-logs (job-0726) is failed` |
| job-0255 | rotate-keys | failed | normal | `level=2 rotate-keys (job-0255) is failed` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
