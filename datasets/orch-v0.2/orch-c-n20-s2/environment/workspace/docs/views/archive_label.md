# Archive Label view

Module: `views/archive_label.py`. Audience: the executive summary email.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0231 | invoice-run | failed | normal | `-- job job-0231 / invoice-run / failed` |
| job-0128 | invoice-run | running | low | `vv job job-0128 / invoice-run / running` |
| job-0584 | purge-cache | running | high | `^^ job job-0584 / purge-cache / running` |
| job-0003 | nightly-backup | running | normal | `-- job job-0003 / nightly-backup / running` |
| job-0360 | sync-inventory | done | high | `^^ job job-0360 / sync-inventory / done` |
| job-0242 | resize-images | failed | normal | `-- job job-0242 / resize-images / failed` |
| job-0240 | sync-inventory | pending | low | `vv job job-0240 / sync-inventory / pending` |
| job-0085 | resize-images | failed | normal | `-- job job-0085 / resize-images / failed` |
| job-0865 | invoice-run | pending | normal | `-- job job-0865 / invoice-run / pending` |
| job-0900 | sync-inventory | done | normal | `-- job job-0900 / sync-inventory / done` |
| job-0493 | nightly-backup | pending | normal | `-- job job-0493 / nightly-backup / pending` |
| job-0802 | purge-cache | done | normal | `-- job job-0802 / purge-cache / done` |
| job-0951 | rebuild-feed | done | normal | `-- job job-0951 / rebuild-feed / done` |
| job-0548 | resize-images | failed | low | `vv job job-0548 / resize-images / failed` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
