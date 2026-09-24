# Discord Embed view

Module: `views/discord_embed.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0233 | reindex-search | pending | high | `PENDING: reindex-search [job-0233] ***` |
| job-0596 | reindex-search | running | normal | `RUNNING: reindex-search [job-0596] **` |
| job-0907 | renew-certs | pending | high | `PENDING: renew-certs [job-0907] ***` |
| job-0901 | nightly-backup | done | normal | `DONE: nightly-backup [job-0901] **` |
| job-0887 | send-digest | running | normal | `RUNNING: send-digest [job-0887] **` |
| job-0529 | send-digest | failed | normal | `FAILED: send-digest [job-0529] **` |
| job-0275 | send-digest | running | normal | `RUNNING: send-digest [job-0275] **` |
| job-0790 | renew-certs | failed | low | `FAILED: renew-certs [job-0790] *` |
| job-0331 | resize-images | done | low | `DONE: resize-images [job-0331] *` |
| job-0862 | send-digest | running | normal | `RUNNING: send-digest [job-0862] **` |
| job-0741 | nightly-backup | done | high | `DONE: nightly-backup [job-0741] ***` |
| job-0470 | export-ledger | failed | low | `FAILED: export-ledger [job-0470] *` |
| job-0954 | rebuild-feed | running | high | `RUNNING: rebuild-feed [job-0954] ***` |
| job-0011 | sync-inventory | done | high | `DONE: sync-inventory [job-0011] ***` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
