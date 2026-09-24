# Chat Bot view

Module: `views/chat_bot.py`. Audience: the finance team's weekly review.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0201 | rebuild-feed | pending | high | `URGENT PENDING: rebuild-feed [job-0201]` |
| job-0805 | resize-images | done | low | `DEFERRABLE DONE: resize-images [job-0805]` |
| job-0714 | resize-images | running | normal | `ROUTINE RUNNING: resize-images [job-0714]` |
| job-0324 | reindex-search | done | low | `DEFERRABLE DONE: reindex-search [job-0324]` |
| job-0475 | rotate-keys | pending | low | `DEFERRABLE PENDING: rotate-keys [job-0475]` |
| job-0581 | rebuild-feed | pending | normal | `ROUTINE PENDING: rebuild-feed [job-0581]` |
| job-0097 | send-digest | pending | normal | `ROUTINE PENDING: send-digest [job-0097]` |
| job-0616 | purge-cache | running | low | `DEFERRABLE RUNNING: purge-cache [job-0616]` |
| job-0688 | renew-certs | done | low | `DEFERRABLE DONE: renew-certs [job-0688]` |
| job-0982 | renew-certs | done | high | `URGENT DONE: renew-certs [job-0982]` |
| job-0054 | sync-inventory | pending | high | `URGENT PENDING: sync-inventory [job-0054]` |
| job-0828 | rebuild-feed | failed | low | `DEFERRABLE FAILED: rebuild-feed [job-0828]` |
| job-0843 | purge-cache | running | low | `DEFERRABLE RUNNING: purge-cache [job-0843]` |
| job-0856 | rotate-keys | running | low | `DEFERRABLE RUNNING: rotate-keys [job-0856]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
