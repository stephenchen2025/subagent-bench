# Html Row view

Module: `views/html_row.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0111 | nightly-backup | failed | low | `FAILED: nightly-backup [job-0111] [LOW]` |
| job-0949 | sync-inventory | pending | low | `PENDING: sync-inventory [job-0949] [LOW]` |
| job-0947 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0947] [HIGH]` |
| job-0390 | rotate-keys | failed | low | `FAILED: rotate-keys [job-0390] [LOW]` |
| job-0538 | resize-images | done | high | `DONE: resize-images [job-0538] [HIGH]` |
| job-0214 | renew-certs | done | normal | `DONE: renew-certs [job-0214] [NORMAL]` |
| job-0867 | rebuild-feed | failed | normal | `FAILED: rebuild-feed [job-0867] [NORMAL]` |
| job-0868 | nightly-backup | failed | normal | `FAILED: nightly-backup [job-0868] [NORMAL]` |
| job-0383 | compact-logs | pending | low | `PENDING: compact-logs [job-0383] [LOW]` |
| job-0297 | rotate-keys | failed | high | `FAILED: rotate-keys [job-0297] [HIGH]` |
| job-0280 | nightly-backup | done | low | `DONE: nightly-backup [job-0280] [LOW]` |
| job-0710 | purge-cache | failed | low | `FAILED: purge-cache [job-0710] [LOW]` |
| job-0159 | purge-cache | done | high | `DONE: purge-cache [job-0159] [HIGH]` |
| job-0515 | export-ledger | running | normal | `RUNNING: export-ledger [job-0515] [NORMAL]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
