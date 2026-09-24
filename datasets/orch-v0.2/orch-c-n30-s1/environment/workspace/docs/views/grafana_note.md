# Grafana Note view

Module: `views/grafana_note.py`. Audience: release managers.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0276 | purge-cache | pending | high | `level=3 job-0276 | purge-cache | pending` |
| job-0600 | invoice-run | pending | normal | `level=2 job-0600 | invoice-run | pending` |
| job-0749 | compact-logs | done | high | `level=3 job-0749 | compact-logs | done` |
| job-0404 | send-digest | running | low | `level=1 job-0404 | send-digest | running` |
| job-0734 | reindex-search | running | low | `level=1 job-0734 | reindex-search | running` |
| job-0953 | rebuild-feed | running | normal | `level=2 job-0953 | rebuild-feed | running` |
| job-0634 | compact-logs | running | low | `level=1 job-0634 | compact-logs | running` |
| job-0005 | send-digest | running | low | `level=1 job-0005 | send-digest | running` |
| job-0763 | compact-logs | done | high | `level=3 job-0763 | compact-logs | done` |
| job-0914 | compact-logs | pending | high | `level=3 job-0914 | compact-logs | pending` |
| job-0573 | nightly-backup | pending | high | `level=3 job-0573 | nightly-backup | pending` |
| job-0726 | rebuild-feed | failed | high | `level=3 job-0726 | rebuild-feed | failed` |
| job-0376 | send-digest | running | high | `level=3 job-0376 | send-digest | running` |
| job-0767 | renew-certs | pending | low | `level=1 job-0767 | renew-certs | pending` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
