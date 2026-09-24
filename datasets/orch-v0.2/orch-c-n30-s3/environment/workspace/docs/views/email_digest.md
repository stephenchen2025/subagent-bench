# Email Digest view

Module: `views/email_digest.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0758 | resize-images | pending | normal | `PENDING: resize-images [job-0758] **` |
| job-0743 | nightly-backup | running | normal | `RUNNING: nightly-backup [job-0743] **` |
| job-0602 | resize-images | done | low | `DONE: resize-images [job-0602] *` |
| job-0428 | invoice-run | failed | low | `FAILED: invoice-run [job-0428] *` |
| job-0376 | resize-images | done | low | `DONE: resize-images [job-0376] *` |
| job-0430 | renew-certs | done | low | `DONE: renew-certs [job-0430] *` |
| job-0126 | rotate-keys | failed | high | `FAILED: rotate-keys [job-0126] ***` |
| job-0967 | rebuild-feed | failed | normal | `FAILED: rebuild-feed [job-0967] **` |
| job-0305 | export-ledger | pending | low | `PENDING: export-ledger [job-0305] *` |
| job-0668 | reindex-search | running | normal | `RUNNING: reindex-search [job-0668] **` |
| job-0168 | rebuild-feed | done | low | `DONE: rebuild-feed [job-0168] *` |
| job-0575 | sync-inventory | done | normal | `DONE: sync-inventory [job-0575] **` |
| job-0904 | renew-certs | running | low | `RUNNING: renew-certs [job-0904] *` |
| job-0839 | resize-images | done | normal | `DONE: resize-images [job-0839] **` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
