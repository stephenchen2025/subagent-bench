# Log Line view

Module: `views/log_line.py`. Audience: customer support leads.

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
| job-0382 | send-digest | pending | high | `*** job-0382 | send-digest | pending` |
| job-0544 | nightly-backup | failed | low | `* job-0544 | nightly-backup | failed` |
| job-0702 | resize-images | done | low | `* job-0702 | resize-images | done` |
| job-0999 | sync-inventory | failed | high | `*** job-0999 | sync-inventory | failed` |
| job-0122 | export-ledger | failed | low | `* job-0122 | export-ledger | failed` |
| job-0639 | purge-cache | running | high | `*** job-0639 | purge-cache | running` |
| job-0891 | sync-inventory | running | normal | `** job-0891 | sync-inventory | running` |
| job-0572 | rotate-keys | done | normal | `** job-0572 | rotate-keys | done` |
| job-0901 | rebuild-feed | done | normal | `** job-0901 | rebuild-feed | done` |
| job-0787 | sync-inventory | done | high | `*** job-0787 | sync-inventory | done` |
| job-0195 | renew-certs | running | high | `*** job-0195 | renew-certs | running` |
| job-0897 | send-digest | pending | low | `* job-0897 | send-digest | pending` |
| job-0685 | compact-logs | failed | high | `*** job-0685 | compact-logs | failed` |
| job-0705 | rebuild-feed | pending | normal | `** job-0705 | rebuild-feed | pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
