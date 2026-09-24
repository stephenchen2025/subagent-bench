# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: customer support leads.

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
| job-0594 | rebuild-feed | done | high | `URGENT DONE: rebuild-feed [job-0594]` |
| job-0356 | reindex-search | running | high | `URGENT RUNNING: reindex-search [job-0356]` |
| job-0017 | resize-images | done | normal | `ROUTINE DONE: resize-images [job-0017]` |
| job-0855 | invoice-run | running | normal | `ROUTINE RUNNING: invoice-run [job-0855]` |
| job-0972 | reindex-search | failed | high | `URGENT FAILED: reindex-search [job-0972]` |
| job-0773 | purge-cache | failed | high | `URGENT FAILED: purge-cache [job-0773]` |
| job-0542 | rotate-keys | failed | normal | `ROUTINE FAILED: rotate-keys [job-0542]` |
| job-0323 | rebuild-feed | pending | low | `DEFERRABLE PENDING: rebuild-feed [job-0323]` |
| job-0933 | invoice-run | pending | high | `URGENT PENDING: invoice-run [job-0933]` |
| job-0374 | rebuild-feed | failed | high | `URGENT FAILED: rebuild-feed [job-0374]` |
| job-0082 | compact-logs | done | normal | `ROUTINE DONE: compact-logs [job-0082]` |
| job-0841 | export-ledger | pending | high | `URGENT PENDING: export-ledger [job-0841]` |
| job-0700 | export-ledger | pending | high | `URGENT PENDING: export-ledger [job-0700]` |
| job-0753 | nightly-backup | pending | low | `DEFERRABLE PENDING: nightly-backup [job-0753]` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
