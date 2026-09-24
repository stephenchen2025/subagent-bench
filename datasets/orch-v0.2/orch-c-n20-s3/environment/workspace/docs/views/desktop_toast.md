# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0086 | export-ledger | done | low | `job job-0086 / export-ledger / done P3` |
| job-0300 | compact-logs | failed | high | `job job-0300 / compact-logs / failed P1` |
| job-0045 | resize-images | failed | high | `job job-0045 / resize-images / failed P1` |
| job-0167 | sync-inventory | running | low | `job job-0167 / sync-inventory / running P3` |
| job-0740 | compact-logs | pending | normal | `job job-0740 / compact-logs / pending P2` |
| job-0964 | reindex-search | done | high | `job job-0964 / reindex-search / done P1` |
| job-0841 | export-ledger | running | normal | `job job-0841 / export-ledger / running P2` |
| job-0385 | export-ledger | failed | low | `job job-0385 / export-ledger / failed P3` |
| job-0682 | nightly-backup | pending | low | `job job-0682 / nightly-backup / pending P3` |
| job-0630 | reindex-search | running | high | `job job-0630 / reindex-search / running P1` |
| job-0722 | reindex-search | done | low | `job job-0722 / reindex-search / done P3` |
| job-0483 | compact-logs | pending | normal | `job job-0483 / compact-logs / pending P2` |
| job-0978 | rebuild-feed | done | normal | `job job-0978 / rebuild-feed / done P2` |
| job-0850 | sync-inventory | failed | low | `job job-0850 / sync-inventory / failed P3` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
