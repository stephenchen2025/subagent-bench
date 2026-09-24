# Markdown List view

Module: `views/markdown_list.py`. Audience: the executive summary email.

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
| job-0386 | purge-cache | done | high | `purge-cache (job-0386) is done URGENT` |
| job-0981 | nightly-backup | pending | low | `nightly-backup (job-0981) is pending DEFERRABLE` |
| job-0206 | resize-images | failed | normal | `resize-images (job-0206) is failed ROUTINE` |
| job-0854 | invoice-run | done | high | `invoice-run (job-0854) is done URGENT` |
| job-0782 | sync-inventory | done | high | `sync-inventory (job-0782) is done URGENT` |
| job-0533 | rebuild-feed | done | low | `rebuild-feed (job-0533) is done DEFERRABLE` |
| job-0080 | renew-certs | done | high | `renew-certs (job-0080) is done URGENT` |
| job-0698 | purge-cache | running | high | `purge-cache (job-0698) is running URGENT` |
| job-0845 | sync-inventory | failed | low | `sync-inventory (job-0845) is failed DEFERRABLE` |
| job-0433 | rotate-keys | done | normal | `rotate-keys (job-0433) is done ROUTINE` |
| job-0517 | resize-images | failed | normal | `resize-images (job-0517) is failed ROUTINE` |
| job-0611 | purge-cache | failed | normal | `purge-cache (job-0611) is failed ROUTINE` |
| job-0309 | nightly-backup | done | high | `nightly-backup (job-0309) is done URGENT` |
| job-0507 | invoice-run | pending | high | `invoice-run (job-0507) is pending URGENT` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
