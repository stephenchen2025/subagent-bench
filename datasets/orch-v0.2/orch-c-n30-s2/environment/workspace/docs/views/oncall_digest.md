# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0629 | invoice-run | pending | low | `job-0629 | invoice-run | pending !` |
| job-0514 | export-ledger | done | low | `job-0514 | export-ledger | done !` |
| job-0574 | compact-logs | pending | low | `job-0574 | compact-logs | pending !` |
| job-0726 | rebuild-feed | pending | low | `job-0726 | rebuild-feed | pending !` |
| job-0751 | resize-images | pending | normal | `job-0751 | resize-images | pending !!` |
| job-0959 | reindex-search | failed | low | `job-0959 | reindex-search | failed !` |
| job-0583 | compact-logs | running | high | `job-0583 | compact-logs | running !!!` |
| job-0427 | reindex-search | pending | low | `job-0427 | reindex-search | pending !` |
| job-0736 | renew-certs | running | normal | `job-0736 | renew-certs | running !!` |
| job-0281 | renew-certs | done | high | `job-0281 | renew-certs | done !!!` |
| job-0021 | compact-logs | done | normal | `job-0021 | compact-logs | done !!` |
| job-0640 | invoice-run | running | normal | `job-0640 | invoice-run | running !!` |
| job-0061 | export-ledger | done | high | `job-0061 | export-ledger | done !!!` |
| job-0597 | resize-images | done | normal | `job-0597 | resize-images | done !!` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
