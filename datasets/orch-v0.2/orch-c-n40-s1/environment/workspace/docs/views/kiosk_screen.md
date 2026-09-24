# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: the platform team's wall display.

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
| job-0832 | reindex-search | running | high | `job-0832: reindex-search -- running color=red` |
| job-0210 | invoice-run | failed | high | `job-0210: invoice-run -- failed color=red` |
| job-0452 | reindex-search | failed | high | `job-0452: reindex-search -- failed color=red` |
| job-0226 | reindex-search | done | high | `job-0226: reindex-search -- done color=red` |
| job-0469 | sync-inventory | running | normal | `job-0469: sync-inventory -- running color=amber` |
| job-0145 | reindex-search | pending | high | `job-0145: reindex-search -- pending color=red` |
| job-0019 | send-digest | done | normal | `job-0019: send-digest -- done color=amber` |
| job-0040 | compact-logs | running | normal | `job-0040: compact-logs -- running color=amber` |
| job-0731 | resize-images | pending | high | `job-0731: resize-images -- pending color=red` |
| job-0908 | rebuild-feed | pending | normal | `job-0908: rebuild-feed -- pending color=amber` |
| job-0682 | export-ledger | pending | low | `job-0682: export-ledger -- pending color=green` |
| job-0293 | compact-logs | pending | high | `job-0293: compact-logs -- pending color=red` |
| job-0160 | compact-logs | done | high | `job-0160: compact-logs -- done color=red` |
| job-0553 | resize-images | done | low | `job-0553: resize-images -- done color=green` |

## History

- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
