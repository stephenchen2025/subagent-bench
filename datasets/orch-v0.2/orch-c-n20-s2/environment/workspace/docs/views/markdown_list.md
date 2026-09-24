# Markdown List view

Module: `views/markdown_list.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0928 | send-digest | running | low | `vv job-0928: send-digest -- running` |
| job-0747 | rotate-keys | running | high | `^^ job-0747: rotate-keys -- running` |
| job-0607 | reindex-search | pending | high | `^^ job-0607: reindex-search -- pending` |
| job-0860 | reindex-search | done | normal | `-- job-0860: reindex-search -- done` |
| job-0410 | export-ledger | done | high | `^^ job-0410: export-ledger -- done` |
| job-0971 | renew-certs | pending | low | `vv job-0971: renew-certs -- pending` |
| job-0569 | rotate-keys | running | low | `vv job-0569: rotate-keys -- running` |
| job-0767 | renew-certs | pending | high | `^^ job-0767: renew-certs -- pending` |
| job-0325 | purge-cache | failed | low | `vv job-0325: purge-cache -- failed` |
| job-0285 | rebuild-feed | running | normal | `-- job-0285: rebuild-feed -- running` |
| job-0996 | nightly-backup | done | high | `^^ job-0996: nightly-backup -- done` |
| job-0298 | nightly-backup | done | normal | `-- job-0298: nightly-backup -- done` |
| job-0175 | send-digest | done | high | `^^ job-0175: send-digest -- done` |
| job-0674 | reindex-search | running | low | `vv job-0674: reindex-search -- running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
