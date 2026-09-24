# Grafana Note view

Module: `views/grafana_note.py`. Audience: the platform team's wall display.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0746 | send-digest | running | low | `color=green job-0746 | send-digest | running` |
| job-0468 | renew-certs | failed | high | `color=red job-0468 | renew-certs | failed` |
| job-0584 | purge-cache | pending | normal | `color=amber job-0584 | purge-cache | pending` |
| job-0062 | compact-logs | failed | normal | `color=amber job-0062 | compact-logs | failed` |
| job-0937 | reindex-search | running | low | `color=green job-0937 | reindex-search | running` |
| job-0845 | rotate-keys | failed | high | `color=red job-0845 | rotate-keys | failed` |
| job-0979 | rebuild-feed | failed | normal | `color=amber job-0979 | rebuild-feed | failed` |
| job-0316 | reindex-search | done | high | `color=red job-0316 | reindex-search | done` |
| job-0800 | rotate-keys | pending | low | `color=green job-0800 | rotate-keys | pending` |
| job-0976 | resize-images | done | normal | `color=amber job-0976 | resize-images | done` |
| job-0799 | reindex-search | failed | low | `color=green job-0799 | reindex-search | failed` |
| job-0462 | renew-certs | failed | high | `color=red job-0462 | renew-certs | failed` |
| job-0733 | invoice-run | failed | high | `color=red job-0733 | invoice-run | failed` |
| job-0926 | compact-logs | running | normal | `color=amber job-0926 | compact-logs | running` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
