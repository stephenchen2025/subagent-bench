# Wiki Table view

Module: `views/wiki_table.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0117 | rebuild-feed | failed | low | `job-0117 | rebuild-feed | failed DEFERRABLE` |
| job-0092 | invoice-run | running | normal | `job-0092 | invoice-run | running ROUTINE` |
| job-0409 | rebuild-feed | pending | high | `job-0409 | rebuild-feed | pending URGENT` |
| job-0695 | rotate-keys | pending | low | `job-0695 | rotate-keys | pending DEFERRABLE` |
| job-0839 | nightly-backup | pending | low | `job-0839 | nightly-backup | pending DEFERRABLE` |
| job-0573 | nightly-backup | pending | high | `job-0573 | nightly-backup | pending URGENT` |
| job-0481 | invoice-run | failed | normal | `job-0481 | invoice-run | failed ROUTINE` |
| job-0953 | reindex-search | done | high | `job-0953 | reindex-search | done URGENT` |
| job-0122 | rebuild-feed | pending | normal | `job-0122 | rebuild-feed | pending ROUTINE` |
| job-0494 | resize-images | failed | low | `job-0494 | resize-images | failed DEFERRABLE` |
| job-0735 | compact-logs | pending | high | `job-0735 | compact-logs | pending URGENT` |
| job-0073 | invoice-run | pending | high | `job-0073 | invoice-run | pending URGENT` |
| job-0303 | send-digest | running | low | `job-0303 | send-digest | running DEFERRABLE` |
| job-0944 | invoice-run | pending | low | `job-0944 | invoice-run | pending DEFERRABLE` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
