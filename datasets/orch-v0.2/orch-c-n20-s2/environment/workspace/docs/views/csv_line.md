# Csv Line view

Module: `views/csv_line.py`. Audience: release managers.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0628 | purge-cache | pending | high | `job-0628: purge-cache -- pending ***` |
| job-0242 | invoice-run | running | high | `job-0242: invoice-run -- running ***` |
| job-0636 | export-ledger | pending | low | `job-0636: export-ledger -- pending *` |
| job-0262 | reindex-search | failed | high | `job-0262: reindex-search -- failed ***` |
| job-0631 | export-ledger | running | normal | `job-0631: export-ledger -- running **` |
| job-0769 | export-ledger | running | high | `job-0769: export-ledger -- running ***` |
| job-0303 | compact-logs | failed | normal | `job-0303: compact-logs -- failed **` |
| job-0586 | export-ledger | failed | low | `job-0586: export-ledger -- failed *` |
| job-0028 | compact-logs | running | normal | `job-0028: compact-logs -- running **` |
| job-0309 | invoice-run | running | high | `job-0309: invoice-run -- running ***` |
| job-0592 | purge-cache | done | low | `job-0592: purge-cache -- done *` |
| job-0354 | purge-cache | running | normal | `job-0354: purge-cache -- running **` |
| job-0900 | rotate-keys | pending | low | `job-0900: rotate-keys -- pending *` |
| job-0897 | resize-images | failed | normal | `job-0897: resize-images -- failed **` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
