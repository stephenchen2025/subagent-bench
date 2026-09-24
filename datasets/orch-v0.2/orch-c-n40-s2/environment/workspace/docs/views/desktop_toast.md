# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: the platform team's wall display.

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
| job-0610 | purge-cache | running | low | `* job job-0610 / purge-cache / running` |
| job-0785 | purge-cache | running | normal | `** job job-0785 / purge-cache / running` |
| job-0741 | rotate-keys | pending | high | `*** job job-0741 / rotate-keys / pending` |
| job-0643 | rotate-keys | done | normal | `** job job-0643 / rotate-keys / done` |
| job-0217 | renew-certs | running | low | `* job job-0217 / renew-certs / running` |
| job-0322 | reindex-search | running | low | `* job job-0322 / reindex-search / running` |
| job-0375 | invoice-run | running | low | `* job job-0375 / invoice-run / running` |
| job-0043 | sync-inventory | failed | low | `* job job-0043 / sync-inventory / failed` |
| job-0648 | send-digest | pending | normal | `** job job-0648 / send-digest / pending` |
| job-0932 | send-digest | done | high | `*** job job-0932 / send-digest / done` |
| job-0505 | send-digest | done | normal | `** job job-0505 / send-digest / done` |
| job-0917 | resize-images | pending | high | `*** job job-0917 / resize-images / pending` |
| job-0977 | send-digest | running | low | `* job job-0977 / send-digest / running` |
| job-0274 | rebuild-feed | done | normal | `** job job-0274 / rebuild-feed / done` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
