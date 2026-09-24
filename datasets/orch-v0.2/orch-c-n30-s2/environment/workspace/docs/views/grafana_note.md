# Grafana Note view

Module: `views/grafana_note.py`. Audience: the executive summary email.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0999 | sync-inventory | failed | low | `* job job-0999 / sync-inventory / failed` |
| job-0807 | compact-logs | running | low | `* job job-0807 / compact-logs / running` |
| job-0232 | renew-certs | done | low | `* job job-0232 / renew-certs / done` |
| job-0134 | sync-inventory | pending | normal | `** job job-0134 / sync-inventory / pending` |
| job-0895 | invoice-run | done | high | `*** job job-0895 / invoice-run / done` |
| job-0164 | nightly-backup | failed | normal | `** job job-0164 / nightly-backup / failed` |
| job-0907 | renew-certs | pending | low | `* job job-0907 / renew-certs / pending` |
| job-0057 | resize-images | running | normal | `** job job-0057 / resize-images / running` |
| job-0626 | purge-cache | done | high | `*** job job-0626 / purge-cache / done` |
| job-0336 | reindex-search | done | normal | `** job job-0336 / reindex-search / done` |
| job-0136 | rebuild-feed | failed | high | `*** job job-0136 / rebuild-feed / failed` |
| job-0554 | rotate-keys | pending | high | `*** job job-0554 / rotate-keys / pending` |
| job-0110 | nightly-backup | failed | normal | `** job job-0110 / nightly-backup / failed` |
| job-0361 | rotate-keys | done | normal | `** job job-0361 / rotate-keys / done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
