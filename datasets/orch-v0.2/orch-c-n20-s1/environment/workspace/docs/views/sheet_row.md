# Sheet Row view

Module: `views/sheet_row.py`. Audience: customer support leads.

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
| job-0400 | nightly-backup | running | high | `job-0400: nightly-backup -- running priority:high` |
| job-0349 | sync-inventory | running | low | `job-0349: sync-inventory -- running priority:low` |
| job-0945 | invoice-run | running | normal | `job-0945: invoice-run -- running priority:normal` |
| job-0055 | purge-cache | failed | normal | `job-0055: purge-cache -- failed priority:normal` |
| job-0715 | export-ledger | pending | high | `job-0715: export-ledger -- pending priority:high` |
| job-0883 | invoice-run | running | low | `job-0883: invoice-run -- running priority:low` |
| job-0262 | purge-cache | failed | normal | `job-0262: purge-cache -- failed priority:normal` |
| job-0923 | export-ledger | failed | low | `job-0923: export-ledger -- failed priority:low` |
| job-0102 | purge-cache | failed | low | `job-0102: purge-cache -- failed priority:low` |
| job-0834 | nightly-backup | failed | normal | `job-0834: nightly-backup -- failed priority:normal` |
| job-0678 | renew-certs | pending | low | `job-0678: renew-certs -- pending priority:low` |
| job-0595 | sync-inventory | done | high | `job-0595: sync-inventory -- done priority:high` |
| job-0877 | invoice-run | done | high | `job-0877: invoice-run -- done priority:high` |
| job-0754 | renew-certs | pending | normal | `job-0754: renew-certs -- pending priority:normal` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
