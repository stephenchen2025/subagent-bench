# Discord Embed view

Module: `views/discord_embed.py`. Audience: the on-call engineer who is paged at night.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0732 | purge-cache | failed | high | `FAILED: purge-cache [job-0732] URGENT` |
| job-0481 | purge-cache | running | low | `RUNNING: purge-cache [job-0481] DEFERRABLE` |
| job-0445 | send-digest | done | normal | `DONE: send-digest [job-0445] ROUTINE` |
| job-0770 | reindex-search | done | low | `DONE: reindex-search [job-0770] DEFERRABLE` |
| job-0584 | export-ledger | done | high | `DONE: export-ledger [job-0584] URGENT` |
| job-0954 | resize-images | running | normal | `RUNNING: resize-images [job-0954] ROUTINE` |
| job-0559 | reindex-search | running | low | `RUNNING: reindex-search [job-0559] DEFERRABLE` |
| job-0958 | renew-certs | pending | normal | `PENDING: renew-certs [job-0958] ROUTINE` |
| job-0370 | purge-cache | pending | low | `PENDING: purge-cache [job-0370] DEFERRABLE` |
| job-0390 | rebuild-feed | done | high | `DONE: rebuild-feed [job-0390] URGENT` |
| job-0988 | reindex-search | running | high | `RUNNING: reindex-search [job-0988] URGENT` |
| job-0173 | sync-inventory | failed | low | `FAILED: sync-inventory [job-0173] DEFERRABLE` |
| job-0976 | export-ledger | failed | low | `FAILED: export-ledger [job-0976] DEFERRABLE` |
| job-0477 | invoice-run | running | normal | `RUNNING: invoice-run [job-0477] ROUTINE` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
