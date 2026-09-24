# Log Line view

Module: `views/log_line.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0720 | compact-logs | running | low | `priority:low job-0720 | compact-logs | running` |
| job-0982 | compact-logs | done | high | `priority:high job-0982 | compact-logs | done` |
| job-0252 | rotate-keys | running | normal | `priority:normal job-0252 | rotate-keys | running` |
| job-0571 | send-digest | pending | low | `priority:low job-0571 | send-digest | pending` |
| job-0587 | reindex-search | failed | high | `priority:high job-0587 | reindex-search | failed` |
| job-0654 | nightly-backup | failed | normal | `priority:normal job-0654 | nightly-backup | failed` |
| job-0855 | resize-images | running | normal | `priority:normal job-0855 | resize-images | running` |
| job-0445 | compact-logs | done | low | `priority:low job-0445 | compact-logs | done` |
| job-0990 | reindex-search | running | high | `priority:high job-0990 | reindex-search | running` |
| job-0466 | rotate-keys | failed | low | `priority:low job-0466 | rotate-keys | failed` |
| job-0975 | invoice-run | done | normal | `priority:normal job-0975 | invoice-run | done` |
| job-0992 | export-ledger | failed | high | `priority:high job-0992 | export-ledger | failed` |
| job-0254 | reindex-search | running | high | `priority:high job-0254 | reindex-search | running` |
| job-0891 | reindex-search | running | normal | `priority:normal job-0891 | reindex-search | running` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
