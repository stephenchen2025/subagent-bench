# Csv Line view

Module: `views/csv_line.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0506 | renew-certs | failed | low | `FAILED: renew-certs [job-0506] DEFERRABLE` |
| job-0967 | invoice-run | failed | high | `FAILED: invoice-run [job-0967] URGENT` |
| job-0657 | purge-cache | running | low | `RUNNING: purge-cache [job-0657] DEFERRABLE` |
| job-0126 | invoice-run | failed | normal | `FAILED: invoice-run [job-0126] ROUTINE` |
| job-0508 | purge-cache | pending | high | `PENDING: purge-cache [job-0508] URGENT` |
| job-0114 | send-digest | running | low | `RUNNING: send-digest [job-0114] DEFERRABLE` |
| job-0417 | sync-inventory | failed | normal | `FAILED: sync-inventory [job-0417] ROUTINE` |
| job-0378 | reindex-search | pending | high | `PENDING: reindex-search [job-0378] URGENT` |
| job-0984 | resize-images | failed | high | `FAILED: resize-images [job-0984] URGENT` |
| job-0701 | rotate-keys | pending | normal | `PENDING: rotate-keys [job-0701] ROUTINE` |
| job-0077 | rebuild-feed | pending | high | `PENDING: rebuild-feed [job-0077] URGENT` |
| job-0226 | resize-images | running | normal | `RUNNING: resize-images [job-0226] ROUTINE` |
| job-0699 | send-digest | running | high | `RUNNING: send-digest [job-0699] URGENT` |
| job-0150 | renew-certs | pending | low | `PENDING: renew-certs [job-0150] DEFERRABLE` |

## History

- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
