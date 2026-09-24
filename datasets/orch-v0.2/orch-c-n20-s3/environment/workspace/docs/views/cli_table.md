# Cli Table view

Module: `views/cli_table.py`. Audience: the on-call engineer who is paged at night.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0022 | rebuild-feed | failed | low | `rebuild-feed (job-0022) is failed color=green` |
| job-0360 | send-digest | pending | high | `send-digest (job-0360) is pending color=red` |
| job-0977 | sync-inventory | done | low | `sync-inventory (job-0977) is done color=green` |
| job-0180 | purge-cache | failed | normal | `purge-cache (job-0180) is failed color=amber` |
| job-0573 | rotate-keys | failed | low | `rotate-keys (job-0573) is failed color=green` |
| job-0473 | resize-images | failed | low | `resize-images (job-0473) is failed color=green` |
| job-0180 | rebuild-feed | done | high | `rebuild-feed (job-0180) is done color=red` |
| job-0925 | rotate-keys | pending | high | `rotate-keys (job-0925) is pending color=red` |
| job-0890 | renew-certs | running | normal | `renew-certs (job-0890) is running color=amber` |
| job-0550 | reindex-search | pending | normal | `reindex-search (job-0550) is pending color=amber` |
| job-0576 | rotate-keys | pending | high | `rotate-keys (job-0576) is pending color=red` |
| job-0166 | resize-images | done | high | `resize-images (job-0166) is done color=red` |
| job-0417 | rebuild-feed | pending | high | `rebuild-feed (job-0417) is pending color=red` |
| job-0411 | rotate-keys | done | normal | `rotate-keys (job-0411) is done color=amber` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
