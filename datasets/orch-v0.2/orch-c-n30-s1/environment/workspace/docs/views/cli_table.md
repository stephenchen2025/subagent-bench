# Cli Table view

Module: `views/cli_table.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0729 | purge-cache | running | low | `purge-cache (job-0729) is running *` |
| job-0015 | rebuild-feed | failed | normal | `rebuild-feed (job-0015) is failed **` |
| job-0395 | rebuild-feed | done | high | `rebuild-feed (job-0395) is done ***` |
| job-0544 | invoice-run | pending | high | `invoice-run (job-0544) is pending ***` |
| job-0839 | rebuild-feed | done | normal | `rebuild-feed (job-0839) is done **` |
| job-0631 | send-digest | failed | normal | `send-digest (job-0631) is failed **` |
| job-0492 | invoice-run | pending | high | `invoice-run (job-0492) is pending ***` |
| job-0183 | invoice-run | running | high | `invoice-run (job-0183) is running ***` |
| job-0178 | reindex-search | pending | normal | `reindex-search (job-0178) is pending **` |
| job-0879 | rotate-keys | failed | normal | `rotate-keys (job-0879) is failed **` |
| job-0087 | sync-inventory | running | high | `sync-inventory (job-0087) is running ***` |
| job-0118 | invoice-run | running | high | `invoice-run (job-0118) is running ***` |
| job-0235 | reindex-search | done | high | `reindex-search (job-0235) is done ***` |
| job-0258 | nightly-backup | done | normal | `nightly-backup (job-0258) is done **` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
