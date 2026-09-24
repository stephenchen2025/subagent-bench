# Pager Line view

Module: `views/pager_line.py`. Audience: mobile users.

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
| job-0972 | send-digest | done | normal | `color=amber job job-0972 / send-digest / done` |
| job-0117 | purge-cache | failed | low | `color=green job job-0117 / purge-cache / failed` |
| job-0819 | nightly-backup | done | high | `color=red job job-0819 / nightly-backup / done` |
| job-0711 | rebuild-feed | running | low | `color=green job job-0711 / rebuild-feed / running` |
| job-0772 | sync-inventory | running | normal | `color=amber job job-0772 / sync-inventory / running` |
| job-0245 | rebuild-feed | failed | high | `color=red job job-0245 / rebuild-feed / failed` |
| job-0807 | renew-certs | running | low | `color=green job job-0807 / renew-certs / running` |
| job-0493 | invoice-run | running | low | `color=green job job-0493 / invoice-run / running` |
| job-0224 | rotate-keys | pending | low | `color=green job job-0224 / rotate-keys / pending` |
| job-0243 | rebuild-feed | failed | normal | `color=amber job job-0243 / rebuild-feed / failed` |
| job-0098 | reindex-search | done | high | `color=red job job-0098 / reindex-search / done` |
| job-0534 | rotate-keys | pending | normal | `color=amber job job-0534 / rotate-keys / pending` |
| job-0079 | nightly-backup | done | low | `color=green job job-0079 / nightly-backup / done` |
| job-0729 | resize-images | failed | normal | `color=amber job job-0729 / resize-images / failed` |

## History

- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
