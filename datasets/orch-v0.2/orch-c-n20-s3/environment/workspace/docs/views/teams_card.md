# Teams Card view

Module: `views/teams_card.py`. Audience: the platform team's wall display.

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
| job-0240 | rotate-keys | done | low | `DONE: rotate-keys [job-0240] color=green` |
| job-0485 | reindex-search | pending | high | `PENDING: reindex-search [job-0485] color=red` |
| job-0698 | resize-images | done | high | `DONE: resize-images [job-0698] color=red` |
| job-0732 | reindex-search | running | low | `RUNNING: reindex-search [job-0732] color=green` |
| job-0358 | purge-cache | pending | low | `PENDING: purge-cache [job-0358] color=green` |
| job-0563 | rebuild-feed | running | high | `RUNNING: rebuild-feed [job-0563] color=red` |
| job-0209 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0209] color=green` |
| job-0680 | compact-logs | running | high | `RUNNING: compact-logs [job-0680] color=red` |
| job-0830 | export-ledger | running | high | `RUNNING: export-ledger [job-0830] color=red` |
| job-0631 | renew-certs | failed | high | `FAILED: renew-certs [job-0631] color=red` |
| job-0739 | rebuild-feed | failed | normal | `FAILED: rebuild-feed [job-0739] color=amber` |
| job-0740 | export-ledger | failed | high | `FAILED: export-ledger [job-0740] color=red` |
| job-0657 | rebuild-feed | running | high | `RUNNING: rebuild-feed [job-0657] color=red` |
| job-0429 | reindex-search | failed | low | `FAILED: reindex-search [job-0429] color=green` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
