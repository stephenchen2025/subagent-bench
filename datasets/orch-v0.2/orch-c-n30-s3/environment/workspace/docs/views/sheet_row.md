# Sheet Row view

Module: `views/sheet_row.py`. Audience: the executive summary email.

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
| job-0116 | compact-logs | pending | normal | `job job-0116 / compact-logs / pending P2` |
| job-0239 | resize-images | done | normal | `job job-0239 / resize-images / done P2` |
| job-0738 | send-digest | failed | low | `job job-0738 / send-digest / failed P3` |
| job-0698 | nightly-backup | pending | normal | `job job-0698 / nightly-backup / pending P2` |
| job-0558 | resize-images | failed | high | `job job-0558 / resize-images / failed P1` |
| job-0499 | compact-logs | done | high | `job job-0499 / compact-logs / done P1` |
| job-0331 | compact-logs | pending | high | `job job-0331 / compact-logs / pending P1` |
| job-0512 | nightly-backup | running | high | `job job-0512 / nightly-backup / running P1` |
| job-0592 | send-digest | pending | high | `job job-0592 / send-digest / pending P1` |
| job-0999 | invoice-run | running | high | `job job-0999 / invoice-run / running P1` |
| job-0298 | purge-cache | pending | normal | `job job-0298 / purge-cache / pending P2` |
| job-0128 | sync-inventory | failed | low | `job job-0128 / sync-inventory / failed P3` |
| job-0050 | rotate-keys | done | high | `job job-0050 / rotate-keys / done P1` |
| job-0700 | rotate-keys | pending | normal | `job job-0700 / rotate-keys / pending P2` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
