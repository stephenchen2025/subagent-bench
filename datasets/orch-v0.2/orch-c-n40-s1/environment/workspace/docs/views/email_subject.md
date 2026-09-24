# Email Subject view

Module: `views/email_subject.py`. Audience: customer support leads.

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
| job-0369 | purge-cache | running | normal | `job-0369 | purge-cache | running !!` |
| job-0057 | sync-inventory | pending | normal | `job-0057 | sync-inventory | pending !!` |
| job-0767 | sync-inventory | done | high | `job-0767 | sync-inventory | done !!!` |
| job-0381 | rebuild-feed | done | low | `job-0381 | rebuild-feed | done !` |
| job-0674 | resize-images | running | low | `job-0674 | resize-images | running !` |
| job-0143 | export-ledger | done | high | `job-0143 | export-ledger | done !!!` |
| job-0377 | nightly-backup | running | normal | `job-0377 | nightly-backup | running !!` |
| job-0599 | reindex-search | pending | normal | `job-0599 | reindex-search | pending !!` |
| job-0250 | rotate-keys | done | normal | `job-0250 | rotate-keys | done !!` |
| job-0341 | renew-certs | running | normal | `job-0341 | renew-certs | running !!` |
| job-0497 | reindex-search | running | low | `job-0497 | reindex-search | running !` |
| job-0999 | rotate-keys | pending | high | `job-0999 | rotate-keys | pending !!!` |
| job-0643 | invoice-run | done | low | `job-0643 | invoice-run | done !` |
| job-0774 | sync-inventory | failed | low | `job-0774 | sync-inventory | failed !` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
