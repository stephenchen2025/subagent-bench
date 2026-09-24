# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0610 | export-ledger | pending | normal | `job-0610: export-ledger -- pending priority:normal` |
| job-0853 | invoice-run | done | low | `job-0853: invoice-run -- done priority:low` |
| job-0070 | send-digest | pending | high | `job-0070: send-digest -- pending priority:high` |
| job-0401 | reindex-search | running | low | `job-0401: reindex-search -- running priority:low` |
| job-0012 | nightly-backup | failed | high | `job-0012: nightly-backup -- failed priority:high` |
| job-0464 | invoice-run | failed | high | `job-0464: invoice-run -- failed priority:high` |
| job-0290 | reindex-search | failed | high | `job-0290: reindex-search -- failed priority:high` |
| job-0671 | rotate-keys | pending | high | `job-0671: rotate-keys -- pending priority:high` |
| job-0651 | sync-inventory | running | high | `job-0651: sync-inventory -- running priority:high` |
| job-0191 | export-ledger | failed | low | `job-0191: export-ledger -- failed priority:low` |
| job-0298 | rebuild-feed | failed | normal | `job-0298: rebuild-feed -- failed priority:normal` |
| job-0989 | rebuild-feed | pending | high | `job-0989: rebuild-feed -- pending priority:high` |
| job-0854 | renew-certs | failed | low | `job-0854: renew-certs -- failed priority:low` |
| job-0216 | send-digest | pending | low | `job-0216: send-digest -- pending priority:low` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
