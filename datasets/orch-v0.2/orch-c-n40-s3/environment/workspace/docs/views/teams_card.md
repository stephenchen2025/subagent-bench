# Teams Card view

Module: `views/teams_card.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0343 | purge-cache | failed | normal | `[NORMAL] purge-cache (job-0343) is failed` |
| job-0188 | resize-images | failed | high | `[HIGH] resize-images (job-0188) is failed` |
| job-0974 | sync-inventory | failed | normal | `[NORMAL] sync-inventory (job-0974) is failed` |
| job-0326 | rotate-keys | pending | low | `[LOW] rotate-keys (job-0326) is pending` |
| job-0623 | invoice-run | running | low | `[LOW] invoice-run (job-0623) is running` |
| job-0442 | reindex-search | done | low | `[LOW] reindex-search (job-0442) is done` |
| job-0412 | compact-logs | pending | low | `[LOW] compact-logs (job-0412) is pending` |
| job-0871 | renew-certs | running | low | `[LOW] renew-certs (job-0871) is running` |
| job-0335 | purge-cache | done | high | `[HIGH] purge-cache (job-0335) is done` |
| job-0581 | compact-logs | pending | normal | `[NORMAL] compact-logs (job-0581) is pending` |
| job-0304 | rebuild-feed | failed | high | `[HIGH] rebuild-feed (job-0304) is failed` |
| job-0299 | reindex-search | pending | normal | `[NORMAL] reindex-search (job-0299) is pending` |
| job-0756 | nightly-backup | done | high | `[HIGH] nightly-backup (job-0756) is done` |
| job-0875 | sync-inventory | done | low | `[LOW] sync-inventory (job-0875) is done` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
