# Sheet Row view

Module: `views/sheet_row.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0656 | invoice-run | pending | low | `invoice-run (job-0656) is pending !` |
| job-0771 | rotate-keys | running | high | `rotate-keys (job-0771) is running !!!` |
| job-0820 | compact-logs | running | normal | `compact-logs (job-0820) is running !!` |
| job-0118 | rebuild-feed | running | normal | `rebuild-feed (job-0118) is running !!` |
| job-0927 | compact-logs | failed | high | `compact-logs (job-0927) is failed !!!` |
| job-0155 | rotate-keys | pending | high | `rotate-keys (job-0155) is pending !!!` |
| job-0092 | send-digest | failed | high | `send-digest (job-0092) is failed !!!` |
| job-0751 | resize-images | pending | normal | `resize-images (job-0751) is pending !!` |
| job-0406 | rebuild-feed | pending | low | `rebuild-feed (job-0406) is pending !` |
| job-0789 | rebuild-feed | done | low | `rebuild-feed (job-0789) is done !` |
| job-0396 | rebuild-feed | running | low | `rebuild-feed (job-0396) is running !` |
| job-0027 | send-digest | done | low | `send-digest (job-0027) is done !` |
| job-0099 | renew-certs | running | low | `renew-certs (job-0099) is running !` |
| job-0658 | rebuild-feed | pending | normal | `rebuild-feed (job-0658) is pending !!` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
