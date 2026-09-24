# Sla Board view

Module: `views/sla_board.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0099 | reindex-search | failed | normal | `job-0099: reindex-search -- failed color=amber` |
| job-0523 | compact-logs | failed | high | `job-0523: compact-logs -- failed color=red` |
| job-0386 | invoice-run | failed | normal | `job-0386: invoice-run -- failed color=amber` |
| job-0559 | compact-logs | done | normal | `job-0559: compact-logs -- done color=amber` |
| job-0065 | reindex-search | failed | normal | `job-0065: reindex-search -- failed color=amber` |
| job-0646 | sync-inventory | running | high | `job-0646: sync-inventory -- running color=red` |
| job-0572 | rotate-keys | running | normal | `job-0572: rotate-keys -- running color=amber` |
| job-0694 | compact-logs | pending | normal | `job-0694: compact-logs -- pending color=amber` |
| job-0947 | resize-images | pending | high | `job-0947: resize-images -- pending color=red` |
| job-0033 | reindex-search | running | low | `job-0033: reindex-search -- running color=green` |
| job-0187 | export-ledger | running | normal | `job-0187: export-ledger -- running color=amber` |
| job-0809 | invoice-run | pending | low | `job-0809: invoice-run -- pending color=green` |
| job-0073 | send-digest | running | high | `job-0073: send-digest -- running color=red` |
| job-0160 | resize-images | done | normal | `job-0160: resize-images -- done color=amber` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
