# Html Row view

Module: `views/html_row.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0156 | export-ledger | running | normal | `level=2 export-ledger (job-0156) is running` |
| job-0410 | resize-images | failed | normal | `level=2 resize-images (job-0410) is failed` |
| job-0478 | rebuild-feed | running | high | `level=3 rebuild-feed (job-0478) is running` |
| job-0475 | rotate-keys | running | high | `level=3 rotate-keys (job-0475) is running` |
| job-0933 | invoice-run | running | low | `level=1 invoice-run (job-0933) is running` |
| job-0842 | export-ledger | failed | high | `level=3 export-ledger (job-0842) is failed` |
| job-0970 | rebuild-feed | pending | high | `level=3 rebuild-feed (job-0970) is pending` |
| job-0719 | nightly-backup | done | high | `level=3 nightly-backup (job-0719) is done` |
| job-0824 | rebuild-feed | running | low | `level=1 rebuild-feed (job-0824) is running` |
| job-0376 | renew-certs | failed | low | `level=1 renew-certs (job-0376) is failed` |
| job-0945 | compact-logs | failed | low | `level=1 compact-logs (job-0945) is failed` |
| job-0096 | renew-certs | pending | normal | `level=2 renew-certs (job-0096) is pending` |
| job-0574 | reindex-search | failed | high | `level=3 reindex-search (job-0574) is failed` |
| job-0909 | nightly-backup | pending | high | `level=3 nightly-backup (job-0909) is pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
