# Archive Label view

Module: `views/archive_label.py`. Audience: the on-call engineer who is paged at night.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0915 | reindex-search | running | high | `RUNNING: reindex-search [job-0915] color=red` |
| job-0867 | resize-images | failed | normal | `FAILED: resize-images [job-0867] color=amber` |
| job-0047 | export-ledger | done | normal | `DONE: export-ledger [job-0047] color=amber` |
| job-0200 | reindex-search | done | low | `DONE: reindex-search [job-0200] color=green` |
| job-0090 | invoice-run | done | normal | `DONE: invoice-run [job-0090] color=amber` |
| job-0252 | reindex-search | done | low | `DONE: reindex-search [job-0252] color=green` |
| job-0214 | export-ledger | running | high | `RUNNING: export-ledger [job-0214] color=red` |
| job-0807 | export-ledger | running | normal | `RUNNING: export-ledger [job-0807] color=amber` |
| job-0460 | export-ledger | failed | high | `FAILED: export-ledger [job-0460] color=red` |
| job-0491 | rebuild-feed | running | normal | `RUNNING: rebuild-feed [job-0491] color=amber` |
| job-0326 | rotate-keys | failed | low | `FAILED: rotate-keys [job-0326] color=green` |
| job-0250 | rebuild-feed | done | low | `DONE: rebuild-feed [job-0250] color=green` |
| job-0334 | export-ledger | pending | normal | `PENDING: export-ledger [job-0334] color=amber` |
| job-0163 | reindex-search | done | high | `DONE: reindex-search [job-0163] color=red` |

## History

- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
