# Status Badge view

Module: `views/status_badge.py`. Audience: release managers.

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
| job-0941 | invoice-run | running | low | `job-0941: invoice-run -- running priority:low` |
| job-0098 | resize-images | running | high | `job-0098: resize-images -- running priority:high` |
| job-0622 | renew-certs | done | high | `job-0622: renew-certs -- done priority:high` |
| job-0471 | rotate-keys | pending | normal | `job-0471: rotate-keys -- pending priority:normal` |
| job-0028 | nightly-backup | running | high | `job-0028: nightly-backup -- running priority:high` |
| job-0689 | send-digest | running | low | `job-0689: send-digest -- running priority:low` |
| job-0042 | export-ledger | failed | normal | `job-0042: export-ledger -- failed priority:normal` |
| job-0504 | compact-logs | failed | normal | `job-0504: compact-logs -- failed priority:normal` |
| job-0217 | rebuild-feed | done | normal | `job-0217: rebuild-feed -- done priority:normal` |
| job-0311 | resize-images | done | high | `job-0311: resize-images -- done priority:high` |
| job-0583 | nightly-backup | done | low | `job-0583: nightly-backup -- done priority:low` |
| job-0947 | purge-cache | pending | normal | `job-0947: purge-cache -- pending priority:normal` |
| job-0067 | reindex-search | done | low | `job-0067: reindex-search -- done priority:low` |
| job-0698 | compact-logs | failed | high | `job-0698: compact-logs -- failed priority:high` |

## History

- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
