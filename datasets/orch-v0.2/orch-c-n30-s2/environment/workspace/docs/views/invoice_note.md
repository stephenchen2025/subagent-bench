# Invoice Note view

Module: `views/invoice_note.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0897 | nightly-backup | done | normal | `priority:normal job-0897: nightly-backup -- done` |
| job-0950 | rotate-keys | pending | high | `priority:high job-0950: rotate-keys -- pending` |
| job-0941 | compact-logs | running | low | `priority:low job-0941: compact-logs -- running` |
| job-0647 | purge-cache | done | high | `priority:high job-0647: purge-cache -- done` |
| job-0760 | resize-images | failed | high | `priority:high job-0760: resize-images -- failed` |
| job-0151 | export-ledger | running | normal | `priority:normal job-0151: export-ledger -- running` |
| job-0723 | invoice-run | running | low | `priority:low job-0723: invoice-run -- running` |
| job-0977 | purge-cache | failed | normal | `priority:normal job-0977: purge-cache -- failed` |
| job-0206 | rebuild-feed | failed | normal | `priority:normal job-0206: rebuild-feed -- failed` |
| job-0935 | sync-inventory | running | high | `priority:high job-0935: sync-inventory -- running` |
| job-0692 | rebuild-feed | failed | low | `priority:low job-0692: rebuild-feed -- failed` |
| job-0620 | sync-inventory | running | high | `priority:high job-0620: sync-inventory -- running` |
| job-0724 | reindex-search | pending | low | `priority:low job-0724: reindex-search -- pending` |
| job-0839 | nightly-backup | pending | normal | `priority:normal job-0839: nightly-backup -- pending` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
