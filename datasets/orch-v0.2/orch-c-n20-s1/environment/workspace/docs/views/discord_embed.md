# Discord Embed view

Module: `views/discord_embed.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0522 | reindex-search | done | normal | `[NORMAL] job-0522 | reindex-search | done` |
| job-0401 | invoice-run | failed | high | `[HIGH] job-0401 | invoice-run | failed` |
| job-0653 | rebuild-feed | failed | high | `[HIGH] job-0653 | rebuild-feed | failed` |
| job-0462 | reindex-search | running | normal | `[NORMAL] job-0462 | reindex-search | running` |
| job-0737 | compact-logs | failed | normal | `[NORMAL] job-0737 | compact-logs | failed` |
| job-0925 | sync-inventory | running | low | `[LOW] job-0925 | sync-inventory | running` |
| job-0074 | send-digest | running | high | `[HIGH] job-0074 | send-digest | running` |
| job-0786 | rotate-keys | done | low | `[LOW] job-0786 | rotate-keys | done` |
| job-0369 | send-digest | done | normal | `[NORMAL] job-0369 | send-digest | done` |
| job-0076 | renew-certs | running | normal | `[NORMAL] job-0076 | renew-certs | running` |
| job-0314 | reindex-search | pending | normal | `[NORMAL] job-0314 | reindex-search | pending` |
| job-0312 | renew-certs | pending | normal | `[NORMAL] job-0312 | renew-certs | pending` |
| job-0591 | renew-certs | pending | normal | `[NORMAL] job-0591 | renew-certs | pending` |
| job-0770 | export-ledger | done | high | `[HIGH] job-0770 | export-ledger | done` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
