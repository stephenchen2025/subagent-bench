# Wiki Table view

Module: `views/wiki_table.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0631 | purge-cache | failed | normal | `color=amber job job-0631 / purge-cache / failed` |
| job-0730 | renew-certs | running | normal | `color=amber job job-0730 / renew-certs / running` |
| job-0973 | nightly-backup | done | normal | `color=amber job job-0973 / nightly-backup / done` |
| job-0756 | resize-images | pending | high | `color=red job job-0756 / resize-images / pending` |
| job-0227 | reindex-search | running | high | `color=red job job-0227 / reindex-search / running` |
| job-0922 | reindex-search | failed | high | `color=red job job-0922 / reindex-search / failed` |
| job-0861 | rotate-keys | done | high | `color=red job job-0861 / rotate-keys / done` |
| job-0536 | rebuild-feed | done | high | `color=red job job-0536 / rebuild-feed / done` |
| job-0367 | resize-images | done | high | `color=red job job-0367 / resize-images / done` |
| job-0617 | send-digest | done | low | `color=green job job-0617 / send-digest / done` |
| job-0852 | purge-cache | running | normal | `color=amber job job-0852 / purge-cache / running` |
| job-0602 | send-digest | failed | low | `color=green job job-0602 / send-digest / failed` |
| job-0481 | sync-inventory | running | low | `color=green job job-0481 / sync-inventory / running` |
| job-0937 | export-ledger | done | high | `color=red job job-0937 / export-ledger / done` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
