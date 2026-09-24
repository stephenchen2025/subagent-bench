# Html Row view

Module: `views/html_row.py`. Audience: the on-call engineer who is paged at night.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0292 | resize-images | running | high | `priority:high job job-0292 / resize-images / running` |
| job-0514 | rotate-keys | done | normal | `priority:normal job job-0514 / rotate-keys / done` |
| job-0914 | renew-certs | failed | normal | `priority:normal job job-0914 / renew-certs / failed` |
| job-0505 | sync-inventory | failed | normal | `priority:normal job job-0505 / sync-inventory / failed` |
| job-0947 | export-ledger | done | normal | `priority:normal job job-0947 / export-ledger / done` |
| job-0520 | invoice-run | running | high | `priority:high job job-0520 / invoice-run / running` |
| job-0313 | invoice-run | pending | low | `priority:low job job-0313 / invoice-run / pending` |
| job-0883 | export-ledger | done | normal | `priority:normal job job-0883 / export-ledger / done` |
| job-0771 | compact-logs | running | normal | `priority:normal job job-0771 / compact-logs / running` |
| job-0985 | nightly-backup | done | low | `priority:low job job-0985 / nightly-backup / done` |
| job-0405 | reindex-search | pending | high | `priority:high job job-0405 / reindex-search / pending` |
| job-0801 | nightly-backup | done | high | `priority:high job job-0801 / nightly-backup / done` |
| job-0681 | resize-images | failed | high | `priority:high job job-0681 / resize-images / failed` |
| job-0912 | export-ledger | pending | normal | `priority:normal job job-0912 / export-ledger / pending` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
