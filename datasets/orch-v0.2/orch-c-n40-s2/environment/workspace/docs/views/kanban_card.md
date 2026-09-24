# Kanban Card view

Module: `views/kanban_card.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0788 | purge-cache | done | low | `purge-cache (job-0788) is done level=1` |
| job-0339 | invoice-run | running | low | `invoice-run (job-0339) is running level=1` |
| job-0884 | rebuild-feed | failed | low | `rebuild-feed (job-0884) is failed level=1` |
| job-0631 | renew-certs | done | low | `renew-certs (job-0631) is done level=1` |
| job-0153 | invoice-run | pending | normal | `invoice-run (job-0153) is pending level=2` |
| job-0967 | purge-cache | running | high | `purge-cache (job-0967) is running level=3` |
| job-0604 | rebuild-feed | failed | normal | `rebuild-feed (job-0604) is failed level=2` |
| job-0610 | rotate-keys | done | low | `rotate-keys (job-0610) is done level=1` |
| job-0485 | sync-inventory | running | high | `sync-inventory (job-0485) is running level=3` |
| job-0044 | compact-logs | pending | normal | `compact-logs (job-0044) is pending level=2` |
| job-0188 | sync-inventory | running | normal | `sync-inventory (job-0188) is running level=2` |
| job-0310 | rebuild-feed | running | low | `rebuild-feed (job-0310) is running level=1` |
| job-0050 | rotate-keys | running | low | `rotate-keys (job-0050) is running level=1` |
| job-0809 | reindex-search | running | normal | `reindex-search (job-0809) is running level=2` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
