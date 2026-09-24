# Sms Brief view

Module: `views/sms_brief.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0796 | rebuild-feed | pending | high | `PENDING: rebuild-feed [job-0796] !!!` |
| job-0735 | reindex-search | pending | high | `PENDING: reindex-search [job-0735] !!!` |
| job-0647 | nightly-backup | running | low | `RUNNING: nightly-backup [job-0647] !` |
| job-0272 | renew-certs | failed | normal | `FAILED: renew-certs [job-0272] !!` |
| job-0529 | rebuild-feed | done | normal | `DONE: rebuild-feed [job-0529] !!` |
| job-0043 | resize-images | running | high | `RUNNING: resize-images [job-0043] !!!` |
| job-0612 | rebuild-feed | failed | low | `FAILED: rebuild-feed [job-0612] !` |
| job-0126 | send-digest | pending | low | `PENDING: send-digest [job-0126] !` |
| job-0390 | purge-cache | failed | low | `FAILED: purge-cache [job-0390] !` |
| job-0962 | export-ledger | pending | normal | `PENDING: export-ledger [job-0962] !!` |
| job-0063 | rotate-keys | done | high | `DONE: rotate-keys [job-0063] !!!` |
| job-0083 | send-digest | pending | normal | `PENDING: send-digest [job-0083] !!` |
| job-0475 | sync-inventory | pending | normal | `PENDING: sync-inventory [job-0475] !!` |
| job-0578 | sync-inventory | running | high | `RUNNING: sync-inventory [job-0578] !!!` |

## History

- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
