# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0271 | compact-logs | done | high | `job job-0271 / compact-logs / done [HIGH]` |
| job-0401 | sync-inventory | pending | low | `job job-0401 / sync-inventory / pending [LOW]` |
| job-0883 | nightly-backup | failed | low | `job job-0883 / nightly-backup / failed [LOW]` |
| job-0861 | rebuild-feed | done | high | `job job-0861 / rebuild-feed / done [HIGH]` |
| job-0844 | compact-logs | failed | low | `job job-0844 / compact-logs / failed [LOW]` |
| job-0050 | compact-logs | done | normal | `job job-0050 / compact-logs / done [NORMAL]` |
| job-0735 | rotate-keys | pending | low | `job job-0735 / rotate-keys / pending [LOW]` |
| job-0497 | rebuild-feed | pending | normal | `job job-0497 / rebuild-feed / pending [NORMAL]` |
| job-0660 | rebuild-feed | done | low | `job job-0660 / rebuild-feed / done [LOW]` |
| job-0563 | rebuild-feed | failed | low | `job job-0563 / rebuild-feed / failed [LOW]` |
| job-0691 | send-digest | running | normal | `job job-0691 / send-digest / running [NORMAL]` |
| job-0537 | sync-inventory | running | low | `job job-0537 / sync-inventory / running [LOW]` |
| job-0444 | invoice-run | failed | high | `job job-0444 / invoice-run / failed [HIGH]` |
| job-0893 | sync-inventory | failed | normal | `job job-0893 / sync-inventory / failed [NORMAL]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
