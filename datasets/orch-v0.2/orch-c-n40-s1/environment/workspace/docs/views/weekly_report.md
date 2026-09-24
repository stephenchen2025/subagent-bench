# Weekly Report view

Module: `views/weekly_report.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0204 | compact-logs | running | normal | `job job-0204 / compact-logs / running color=amber` |
| job-0810 | sync-inventory | running | normal | `job job-0810 / sync-inventory / running color=amber` |
| job-0054 | export-ledger | failed | normal | `job job-0054 / export-ledger / failed color=amber` |
| job-0740 | export-ledger | running | low | `job job-0740 / export-ledger / running color=green` |
| job-0002 | renew-certs | failed | low | `job job-0002 / renew-certs / failed color=green` |
| job-0149 | export-ledger | failed | normal | `job job-0149 / export-ledger / failed color=amber` |
| job-0080 | rebuild-feed | failed | normal | `job job-0080 / rebuild-feed / failed color=amber` |
| job-0396 | purge-cache | failed | normal | `job job-0396 / purge-cache / failed color=amber` |
| job-0018 | sync-inventory | failed | normal | `job job-0018 / sync-inventory / failed color=amber` |
| job-0923 | rebuild-feed | failed | high | `job job-0923 / rebuild-feed / failed color=red` |
| job-0196 | rebuild-feed | running | low | `job job-0196 / rebuild-feed / running color=green` |
| job-0308 | purge-cache | pending | high | `job job-0308 / purge-cache / pending color=red` |
| job-0579 | send-digest | pending | low | `job job-0579 / send-digest / pending color=green` |
| job-0413 | rotate-keys | failed | normal | `job job-0413 / rotate-keys / failed color=amber` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
