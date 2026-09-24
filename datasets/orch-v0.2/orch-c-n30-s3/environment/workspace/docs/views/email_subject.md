# Email Subject view

Module: `views/email_subject.py`. Audience: customer support leads.

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
| job-0422 | compact-logs | pending | normal | `** job-0422 | compact-logs | pending` |
| job-0452 | invoice-run | failed | normal | `** job-0452 | invoice-run | failed` |
| job-0835 | resize-images | done | normal | `** job-0835 | resize-images | done` |
| job-0723 | renew-certs | done | normal | `** job-0723 | renew-certs | done` |
| job-0979 | rebuild-feed | pending | normal | `** job-0979 | rebuild-feed | pending` |
| job-0681 | send-digest | pending | high | `*** job-0681 | send-digest | pending` |
| job-0704 | invoice-run | pending | normal | `** job-0704 | invoice-run | pending` |
| job-0958 | sync-inventory | running | high | `*** job-0958 | sync-inventory | running` |
| job-0942 | purge-cache | done | low | `* job-0942 | purge-cache | done` |
| job-0471 | reindex-search | failed | normal | `** job-0471 | reindex-search | failed` |
| job-0570 | sync-inventory | done | high | `*** job-0570 | sync-inventory | done` |
| job-0626 | rebuild-feed | done | high | `*** job-0626 | rebuild-feed | done` |
| job-0787 | resize-images | running | low | `* job-0787 | resize-images | running` |
| job-0557 | sync-inventory | running | high | `*** job-0557 | sync-inventory | running` |

## History

- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
