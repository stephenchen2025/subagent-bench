# Discord Embed view

Module: `views/discord_embed.py`. Audience: customer support leads.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0649 | purge-cache | running | high | `purge-cache (job-0649) is running URGENT` |
| job-0563 | send-digest | done | low | `send-digest (job-0563) is done DEFERRABLE` |
| job-0521 | invoice-run | failed | low | `invoice-run (job-0521) is failed DEFERRABLE` |
| job-0080 | nightly-backup | done | low | `nightly-backup (job-0080) is done DEFERRABLE` |
| job-0242 | compact-logs | running | low | `compact-logs (job-0242) is running DEFERRABLE` |
| job-0908 | purge-cache | running | normal | `purge-cache (job-0908) is running ROUTINE` |
| job-0117 | resize-images | failed | low | `resize-images (job-0117) is failed DEFERRABLE` |
| job-0755 | rebuild-feed | running | normal | `rebuild-feed (job-0755) is running ROUTINE` |
| job-0198 | export-ledger | running | low | `export-ledger (job-0198) is running DEFERRABLE` |
| job-0761 | reindex-search | done | normal | `reindex-search (job-0761) is done ROUTINE` |
| job-0122 | rotate-keys | failed | low | `rotate-keys (job-0122) is failed DEFERRABLE` |
| job-0543 | send-digest | done | low | `send-digest (job-0543) is done DEFERRABLE` |
| job-0071 | export-ledger | running | high | `export-ledger (job-0071) is running URGENT` |
| job-0301 | rebuild-feed | failed | normal | `rebuild-feed (job-0301) is failed ROUTINE` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
