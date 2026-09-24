# Csv Line view

Module: `views/csv_line.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0719 | send-digest | pending | normal | `P2 send-digest (job-0719) is pending` |
| job-0434 | rotate-keys | running | low | `P3 rotate-keys (job-0434) is running` |
| job-0706 | sync-inventory | done | low | `P3 sync-inventory (job-0706) is done` |
| job-0625 | rebuild-feed | pending | high | `P1 rebuild-feed (job-0625) is pending` |
| job-0700 | invoice-run | pending | high | `P1 invoice-run (job-0700) is pending` |
| job-0578 | invoice-run | failed | low | `P3 invoice-run (job-0578) is failed` |
| job-0463 | rebuild-feed | done | high | `P1 rebuild-feed (job-0463) is done` |
| job-0959 | rebuild-feed | pending | normal | `P2 rebuild-feed (job-0959) is pending` |
| job-0204 | send-digest | pending | high | `P1 send-digest (job-0204) is pending` |
| job-0822 | resize-images | pending | high | `P1 resize-images (job-0822) is pending` |
| job-0125 | reindex-search | failed | normal | `P2 reindex-search (job-0125) is failed` |
| job-0742 | rotate-keys | failed | normal | `P2 rotate-keys (job-0742) is failed` |
| job-0618 | compact-logs | running | high | `P1 compact-logs (job-0618) is running` |
| job-0284 | rotate-keys | running | high | `P1 rotate-keys (job-0284) is running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
