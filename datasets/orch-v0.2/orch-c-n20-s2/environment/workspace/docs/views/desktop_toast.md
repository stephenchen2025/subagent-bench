# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: the on-call engineer who is paged at night.

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
| job-0163 | resize-images | pending | normal | `[NORMAL] resize-images (job-0163) is pending` |
| job-0300 | renew-certs | pending | high | `[HIGH] renew-certs (job-0300) is pending` |
| job-0048 | sync-inventory | done | low | `[LOW] sync-inventory (job-0048) is done` |
| job-0919 | sync-inventory | failed | high | `[HIGH] sync-inventory (job-0919) is failed` |
| job-0990 | nightly-backup | running | normal | `[NORMAL] nightly-backup (job-0990) is running` |
| job-0065 | sync-inventory | done | high | `[HIGH] sync-inventory (job-0065) is done` |
| job-0249 | sync-inventory | running | normal | `[NORMAL] sync-inventory (job-0249) is running` |
| job-0519 | rebuild-feed | pending | normal | `[NORMAL] rebuild-feed (job-0519) is pending` |
| job-0969 | send-digest | done | high | `[HIGH] send-digest (job-0969) is done` |
| job-0823 | compact-logs | pending | normal | `[NORMAL] compact-logs (job-0823) is pending` |
| job-0706 | purge-cache | running | low | `[LOW] purge-cache (job-0706) is running` |
| job-0818 | resize-images | failed | low | `[LOW] resize-images (job-0818) is failed` |
| job-0333 | reindex-search | failed | high | `[HIGH] reindex-search (job-0333) is failed` |
| job-0713 | sync-inventory | failed | normal | `[NORMAL] sync-inventory (job-0713) is failed` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
