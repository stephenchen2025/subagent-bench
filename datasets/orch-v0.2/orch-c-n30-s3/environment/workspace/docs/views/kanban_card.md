# Kanban Card view

Module: `views/kanban_card.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0488 | renew-certs | pending | low | `job-0488: renew-certs -- pending DEFERRABLE` |
| job-0211 | reindex-search | pending | normal | `job-0211: reindex-search -- pending ROUTINE` |
| job-0602 | rebuild-feed | running | high | `job-0602: rebuild-feed -- running URGENT` |
| job-0268 | reindex-search | done | normal | `job-0268: reindex-search -- done ROUTINE` |
| job-0059 | sync-inventory | failed | low | `job-0059: sync-inventory -- failed DEFERRABLE` |
| job-0077 | reindex-search | pending | high | `job-0077: reindex-search -- pending URGENT` |
| job-0962 | rebuild-feed | running | low | `job-0962: rebuild-feed -- running DEFERRABLE` |
| job-0288 | compact-logs | done | normal | `job-0288: compact-logs -- done ROUTINE` |
| job-0651 | sync-inventory | done | high | `job-0651: sync-inventory -- done URGENT` |
| job-0677 | export-ledger | pending | normal | `job-0677: export-ledger -- pending ROUTINE` |
| job-0752 | rebuild-feed | done | high | `job-0752: rebuild-feed -- done URGENT` |
| job-0907 | invoice-run | running | low | `job-0907: invoice-run -- running DEFERRABLE` |
| job-0365 | purge-cache | failed | normal | `job-0365: purge-cache -- failed ROUTINE` |
| job-0934 | compact-logs | running | normal | `job-0934: compact-logs -- running ROUTINE` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
