# Rss Item view

Module: `views/rss_item.py`. Audience: the on-call engineer who is paged at night.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0173 | compact-logs | failed | high | `job job-0173 / compact-logs / failed URGENT` |
| job-0957 | rebuild-feed | done | high | `job job-0957 / rebuild-feed / done URGENT` |
| job-0190 | sync-inventory | failed | normal | `job job-0190 / sync-inventory / failed ROUTINE` |
| job-0987 | reindex-search | failed | high | `job job-0987 / reindex-search / failed URGENT` |
| job-0226 | invoice-run | done | low | `job job-0226 / invoice-run / done DEFERRABLE` |
| job-0816 | rotate-keys | pending | high | `job job-0816 / rotate-keys / pending URGENT` |
| job-0394 | invoice-run | done | high | `job job-0394 / invoice-run / done URGENT` |
| job-0348 | sync-inventory | pending | normal | `job job-0348 / sync-inventory / pending ROUTINE` |
| job-0263 | send-digest | failed | normal | `job job-0263 / send-digest / failed ROUTINE` |
| job-0144 | rotate-keys | failed | normal | `job job-0144 / rotate-keys / failed ROUTINE` |
| job-0662 | sync-inventory | done | low | `job job-0662 / sync-inventory / done DEFERRABLE` |
| job-0913 | sync-inventory | failed | low | `job job-0913 / sync-inventory / failed DEFERRABLE` |
| job-0524 | send-digest | done | high | `job job-0524 / send-digest / done URGENT` |
| job-0010 | reindex-search | running | high | `job job-0010 / reindex-search / running URGENT` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
