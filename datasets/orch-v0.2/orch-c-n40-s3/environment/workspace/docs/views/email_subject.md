# Email Subject view

Module: `views/email_subject.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0331 | reindex-search | pending | high | `reindex-search (job-0331) is pending color=red` |
| job-0819 | nightly-backup | running | low | `nightly-backup (job-0819) is running color=green` |
| job-0544 | purge-cache | done | normal | `purge-cache (job-0544) is done color=amber` |
| job-0219 | rebuild-feed | pending | low | `rebuild-feed (job-0219) is pending color=green` |
| job-0413 | resize-images | running | low | `resize-images (job-0413) is running color=green` |
| job-0949 | resize-images | done | low | `resize-images (job-0949) is done color=green` |
| job-0030 | renew-certs | pending | high | `renew-certs (job-0030) is pending color=red` |
| job-0741 | compact-logs | running | low | `compact-logs (job-0741) is running color=green` |
| job-0394 | nightly-backup | failed | high | `nightly-backup (job-0394) is failed color=red` |
| job-0776 | rotate-keys | pending | normal | `rotate-keys (job-0776) is pending color=amber` |
| job-0459 | resize-images | pending | normal | `resize-images (job-0459) is pending color=amber` |
| job-0633 | rebuild-feed | running | low | `rebuild-feed (job-0633) is running color=green` |
| job-0449 | renew-certs | pending | low | `renew-certs (job-0449) is pending color=green` |
| job-0674 | resize-images | pending | high | `resize-images (job-0674) is pending color=red` |

## History

- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
