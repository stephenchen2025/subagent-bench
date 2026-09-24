# Markdown List view

Module: `views/markdown_list.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0181 | renew-certs | done | normal | `DONE: renew-certs [job-0181] --` |
| job-0324 | reindex-search | running | normal | `RUNNING: reindex-search [job-0324] --` |
| job-0028 | purge-cache | failed | normal | `FAILED: purge-cache [job-0028] --` |
| job-0888 | renew-certs | running | normal | `RUNNING: renew-certs [job-0888] --` |
| job-0007 | export-ledger | done | low | `DONE: export-ledger [job-0007] vv` |
| job-0066 | invoice-run | pending | normal | `PENDING: invoice-run [job-0066] --` |
| job-0964 | export-ledger | failed | high | `FAILED: export-ledger [job-0964] ^^` |
| job-0851 | reindex-search | running | high | `RUNNING: reindex-search [job-0851] ^^` |
| job-0063 | resize-images | pending | low | `PENDING: resize-images [job-0063] vv` |
| job-0517 | send-digest | running | low | `RUNNING: send-digest [job-0517] vv` |
| job-0167 | rebuild-feed | pending | low | `PENDING: rebuild-feed [job-0167] vv` |
| job-0255 | purge-cache | done | low | `DONE: purge-cache [job-0255] vv` |
| job-0569 | nightly-backup | failed | high | `FAILED: nightly-backup [job-0569] ^^` |
| job-0671 | reindex-search | pending | low | `PENDING: reindex-search [job-0671] vv` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
