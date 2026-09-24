# Pager Line view

Module: `views/pager_line.py`. Audience: mobile users.

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
| job-0704 | resize-images | done | high | `^^ job-0704: resize-images -- done` |
| job-0044 | send-digest | done | low | `vv job-0044: send-digest -- done` |
| job-0546 | resize-images | pending | normal | `-- job-0546: resize-images -- pending` |
| job-0402 | reindex-search | failed | low | `vv job-0402: reindex-search -- failed` |
| job-0510 | rebuild-feed | pending | high | `^^ job-0510: rebuild-feed -- pending` |
| job-0398 | invoice-run | done | normal | `-- job-0398: invoice-run -- done` |
| job-0010 | sync-inventory | done | low | `vv job-0010: sync-inventory -- done` |
| job-0603 | purge-cache | failed | normal | `-- job-0603: purge-cache -- failed` |
| job-0135 | rebuild-feed | done | low | `vv job-0135: rebuild-feed -- done` |
| job-0412 | send-digest | running | normal | `-- job-0412: send-digest -- running` |
| job-0813 | export-ledger | running | low | `vv job-0813: export-ledger -- running` |
| job-0386 | nightly-backup | failed | normal | `-- job-0386: nightly-backup -- failed` |
| job-0379 | invoice-run | running | normal | `-- job-0379: invoice-run -- running` |
| job-0687 | nightly-backup | pending | low | `vv job-0687: nightly-backup -- pending` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
