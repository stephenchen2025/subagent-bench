# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: customer support leads.

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
| job-0131 | nightly-backup | pending | normal | `job-0131: nightly-backup -- pending priority:normal` |
| job-0218 | sync-inventory | failed | high | `job-0218: sync-inventory -- failed priority:high` |
| job-0258 | purge-cache | failed | normal | `job-0258: purge-cache -- failed priority:normal` |
| job-0827 | purge-cache | done | high | `job-0827: purge-cache -- done priority:high` |
| job-0067 | resize-images | running | high | `job-0067: resize-images -- running priority:high` |
| job-0924 | nightly-backup | done | high | `job-0924: nightly-backup -- done priority:high` |
| job-0921 | send-digest | done | normal | `job-0921: send-digest -- done priority:normal` |
| job-0944 | rotate-keys | failed | normal | `job-0944: rotate-keys -- failed priority:normal` |
| job-0659 | rotate-keys | done | low | `job-0659: rotate-keys -- done priority:low` |
| job-0730 | export-ledger | done | high | `job-0730: export-ledger -- done priority:high` |
| job-0271 | reindex-search | failed | low | `job-0271: reindex-search -- failed priority:low` |
| job-0339 | rotate-keys | pending | high | `job-0339: rotate-keys -- pending priority:high` |
| job-0676 | sync-inventory | done | high | `job-0676: sync-inventory -- done priority:high` |
| job-0484 | resize-images | failed | low | `job-0484: resize-images -- failed priority:low` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
