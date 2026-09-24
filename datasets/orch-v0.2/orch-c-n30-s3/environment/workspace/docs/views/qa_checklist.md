# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: customer support leads.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0535 | reindex-search | pending | low | `vv PENDING: reindex-search [job-0535]` |
| job-0884 | sync-inventory | pending | normal | `-- PENDING: sync-inventory [job-0884]` |
| job-0768 | rebuild-feed | failed | normal | `-- FAILED: rebuild-feed [job-0768]` |
| job-0750 | invoice-run | done | low | `vv DONE: invoice-run [job-0750]` |
| job-0221 | export-ledger | pending | normal | `-- PENDING: export-ledger [job-0221]` |
| job-0888 | nightly-backup | done | low | `vv DONE: nightly-backup [job-0888]` |
| job-0073 | purge-cache | running | normal | `-- RUNNING: purge-cache [job-0073]` |
| job-0174 | send-digest | failed | high | `^^ FAILED: send-digest [job-0174]` |
| job-0110 | rotate-keys | done | low | `vv DONE: rotate-keys [job-0110]` |
| job-0049 | invoice-run | running | normal | `-- RUNNING: invoice-run [job-0049]` |
| job-0988 | export-ledger | failed | low | `vv FAILED: export-ledger [job-0988]` |
| job-0148 | rebuild-feed | pending | low | `vv PENDING: rebuild-feed [job-0148]` |
| job-0521 | reindex-search | failed | normal | `-- FAILED: reindex-search [job-0521]` |
| job-0289 | reindex-search | pending | high | `^^ PENDING: reindex-search [job-0289]` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
