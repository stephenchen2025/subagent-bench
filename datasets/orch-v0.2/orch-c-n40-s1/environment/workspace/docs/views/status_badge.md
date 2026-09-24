# Status Badge view

Module: `views/status_badge.py`. Audience: customer support leads.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0316 | invoice-run | failed | high | `!!! invoice-run (job-0316) is failed` |
| job-0201 | compact-logs | running | high | `!!! compact-logs (job-0201) is running` |
| job-0088 | send-digest | done | high | `!!! send-digest (job-0088) is done` |
| job-0765 | rebuild-feed | running | normal | `!! rebuild-feed (job-0765) is running` |
| job-0335 | send-digest | pending | low | `! send-digest (job-0335) is pending` |
| job-0611 | rotate-keys | failed | high | `!!! rotate-keys (job-0611) is failed` |
| job-0656 | invoice-run | pending | low | `! invoice-run (job-0656) is pending` |
| job-0928 | sync-inventory | pending | normal | `!! sync-inventory (job-0928) is pending` |
| job-0251 | invoice-run | running | normal | `!! invoice-run (job-0251) is running` |
| job-0111 | reindex-search | pending | normal | `!! reindex-search (job-0111) is pending` |
| job-0093 | purge-cache | failed | high | `!!! purge-cache (job-0093) is failed` |
| job-0272 | compact-logs | done | normal | `!! compact-logs (job-0272) is done` |
| job-0979 | nightly-backup | pending | low | `! nightly-backup (job-0979) is pending` |
| job-0720 | rotate-keys | running | normal | `!! rotate-keys (job-0720) is running` |

## History

- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
