# Markdown List view

Module: `views/markdown_list.py`. Audience: customer support leads.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0447 | invoice-run | failed | high | `FAILED: invoice-run [job-0447] !!!` |
| job-0276 | rebuild-feed | running | normal | `RUNNING: rebuild-feed [job-0276] !!` |
| job-0008 | resize-images | done | high | `DONE: resize-images [job-0008] !!!` |
| job-0431 | rotate-keys | pending | high | `PENDING: rotate-keys [job-0431] !!!` |
| job-0266 | rebuild-feed | done | high | `DONE: rebuild-feed [job-0266] !!!` |
| job-0832 | renew-certs | done | high | `DONE: renew-certs [job-0832] !!!` |
| job-0928 | renew-certs | running | high | `RUNNING: renew-certs [job-0928] !!!` |
| job-0514 | rotate-keys | running | high | `RUNNING: rotate-keys [job-0514] !!!` |
| job-0558 | rebuild-feed | done | low | `DONE: rebuild-feed [job-0558] !` |
| job-0110 | compact-logs | running | high | `RUNNING: compact-logs [job-0110] !!!` |
| job-0539 | reindex-search | running | normal | `RUNNING: reindex-search [job-0539] !!` |
| job-0220 | sync-inventory | pending | high | `PENDING: sync-inventory [job-0220] !!!` |
| job-0986 | reindex-search | failed | low | `FAILED: reindex-search [job-0986] !` |
| job-0770 | invoice-run | pending | low | `PENDING: invoice-run [job-0770] !` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
