# Rss Item view

Module: `views/rss_item.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0463 | rebuild-feed | failed | high | `job-0463 | rebuild-feed | failed !!!` |
| job-0691 | sync-inventory | done | normal | `job-0691 | sync-inventory | done !!` |
| job-0747 | send-digest | running | high | `job-0747 | send-digest | running !!!` |
| job-0115 | rotate-keys | failed | high | `job-0115 | rotate-keys | failed !!!` |
| job-0931 | rotate-keys | failed | high | `job-0931 | rotate-keys | failed !!!` |
| job-0641 | rotate-keys | pending | normal | `job-0641 | rotate-keys | pending !!` |
| job-0379 | compact-logs | pending | low | `job-0379 | compact-logs | pending !` |
| job-0223 | rebuild-feed | running | normal | `job-0223 | rebuild-feed | running !!` |
| job-0166 | reindex-search | done | low | `job-0166 | reindex-search | done !` |
| job-0763 | nightly-backup | done | low | `job-0763 | nightly-backup | done !` |
| job-0229 | nightly-backup | done | low | `job-0229 | nightly-backup | done !` |
| job-0838 | renew-certs | done | high | `job-0838 | renew-certs | done !!!` |
| job-0841 | rebuild-feed | running | high | `job-0841 | rebuild-feed | running !!!` |
| job-0076 | resize-images | running | high | `job-0076 | resize-images | running !!!` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
