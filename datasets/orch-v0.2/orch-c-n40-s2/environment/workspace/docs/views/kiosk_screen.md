# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0568 | compact-logs | running | high | `[HIGH] job-0568 | compact-logs | running` |
| job-0351 | reindex-search | failed | low | `[LOW] job-0351 | reindex-search | failed` |
| job-0515 | reindex-search | running | high | `[HIGH] job-0515 | reindex-search | running` |
| job-0086 | purge-cache | done | high | `[HIGH] job-0086 | purge-cache | done` |
| job-0115 | compact-logs | pending | high | `[HIGH] job-0115 | compact-logs | pending` |
| job-0674 | invoice-run | failed | normal | `[NORMAL] job-0674 | invoice-run | failed` |
| job-0301 | nightly-backup | done | low | `[LOW] job-0301 | nightly-backup | done` |
| job-0105 | rebuild-feed | pending | low | `[LOW] job-0105 | rebuild-feed | pending` |
| job-0058 | reindex-search | failed | normal | `[NORMAL] job-0058 | reindex-search | failed` |
| job-0950 | purge-cache | failed | low | `[LOW] job-0950 | purge-cache | failed` |
| job-0928 | rotate-keys | failed | normal | `[NORMAL] job-0928 | rotate-keys | failed` |
| job-0276 | rotate-keys | failed | normal | `[NORMAL] job-0276 | rotate-keys | failed` |
| job-0783 | nightly-backup | done | high | `[HIGH] job-0783 | nightly-backup | done` |
| job-0910 | purge-cache | failed | low | `[LOW] job-0910 | purge-cache | failed` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
