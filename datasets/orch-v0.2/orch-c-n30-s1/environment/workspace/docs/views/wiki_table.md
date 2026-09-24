# Wiki Table view

Module: `views/wiki_table.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0718 | export-ledger | done | normal | `job-0718: export-ledger -- done **` |
| job-0901 | compact-logs | failed | low | `job-0901: compact-logs -- failed *` |
| job-0362 | invoice-run | done | low | `job-0362: invoice-run -- done *` |
| job-0428 | send-digest | failed | high | `job-0428: send-digest -- failed ***` |
| job-0108 | nightly-backup | running | low | `job-0108: nightly-backup -- running *` |
| job-0999 | rotate-keys | running | low | `job-0999: rotate-keys -- running *` |
| job-0441 | nightly-backup | failed | low | `job-0441: nightly-backup -- failed *` |
| job-0359 | invoice-run | done | normal | `job-0359: invoice-run -- done **` |
| job-0930 | invoice-run | pending | high | `job-0930: invoice-run -- pending ***` |
| job-0638 | export-ledger | running | normal | `job-0638: export-ledger -- running **` |
| job-0853 | rotate-keys | failed | low | `job-0853: rotate-keys -- failed *` |
| job-0830 | rotate-keys | running | high | `job-0830: rotate-keys -- running ***` |
| job-0220 | sync-inventory | done | low | `job-0220: sync-inventory -- done *` |
| job-0457 | reindex-search | failed | low | `job-0457: reindex-search -- failed *` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
