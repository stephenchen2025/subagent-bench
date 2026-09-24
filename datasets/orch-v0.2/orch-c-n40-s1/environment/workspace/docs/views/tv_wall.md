# Tv Wall view

Module: `views/tv_wall.py`. Audience: release managers.

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
| job-0398 | purge-cache | failed | high | `job-0398: purge-cache -- failed priority:high` |
| job-0188 | sync-inventory | running | high | `job-0188: sync-inventory -- running priority:high` |
| job-0606 | compact-logs | pending | high | `job-0606: compact-logs -- pending priority:high` |
| job-0117 | rotate-keys | running | normal | `job-0117: rotate-keys -- running priority:normal` |
| job-0388 | rebuild-feed | pending | normal | `job-0388: rebuild-feed -- pending priority:normal` |
| job-0033 | purge-cache | running | low | `job-0033: purge-cache -- running priority:low` |
| job-0853 | sync-inventory | done | normal | `job-0853: sync-inventory -- done priority:normal` |
| job-0438 | nightly-backup | pending | high | `job-0438: nightly-backup -- pending priority:high` |
| job-0060 | nightly-backup | running | high | `job-0060: nightly-backup -- running priority:high` |
| job-0480 | nightly-backup | pending | normal | `job-0480: nightly-backup -- pending priority:normal` |
| job-0810 | export-ledger | failed | high | `job-0810: export-ledger -- failed priority:high` |
| job-0673 | compact-logs | pending | low | `job-0673: compact-logs -- pending priority:low` |
| job-0848 | resize-images | done | low | `job-0848: resize-images -- done priority:low` |
| job-0546 | send-digest | failed | normal | `job-0546: send-digest -- failed priority:normal` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
