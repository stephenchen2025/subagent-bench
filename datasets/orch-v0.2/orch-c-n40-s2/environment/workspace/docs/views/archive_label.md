# Archive Label view

Module: `views/archive_label.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0805 | compact-logs | done | low | `* job-0805 | compact-logs | done` |
| job-0667 | send-digest | done | low | `* job-0667 | send-digest | done` |
| job-0297 | renew-certs | done | low | `* job-0297 | renew-certs | done` |
| job-0160 | sync-inventory | failed | normal | `** job-0160 | sync-inventory | failed` |
| job-0209 | purge-cache | done | low | `* job-0209 | purge-cache | done` |
| job-0199 | rotate-keys | running | low | `* job-0199 | rotate-keys | running` |
| job-0553 | reindex-search | running | high | `*** job-0553 | reindex-search | running` |
| job-0878 | reindex-search | pending | low | `* job-0878 | reindex-search | pending` |
| job-0649 | sync-inventory | failed | normal | `** job-0649 | sync-inventory | failed` |
| job-0873 | reindex-search | pending | normal | `** job-0873 | reindex-search | pending` |
| job-0049 | renew-certs | failed | normal | `** job-0049 | renew-certs | failed` |
| job-0916 | rotate-keys | done | high | `*** job-0916 | rotate-keys | done` |
| job-0233 | resize-images | running | low | `* job-0233 | resize-images | running` |
| job-0703 | purge-cache | done | normal | `** job-0703 | purge-cache | done` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
