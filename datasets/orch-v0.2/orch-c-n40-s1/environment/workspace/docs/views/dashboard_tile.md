# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: the on-call engineer who is paged at night.

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
| job-0597 | renew-certs | done | normal | `job-0597: renew-certs -- done priority:normal` |
| job-0727 | export-ledger | running | high | `job-0727: export-ledger -- running priority:high` |
| job-0470 | compact-logs | running | normal | `job-0470: compact-logs -- running priority:normal` |
| job-0576 | sync-inventory | running | normal | `job-0576: sync-inventory -- running priority:normal` |
| job-0135 | resize-images | done | normal | `job-0135: resize-images -- done priority:normal` |
| job-0553 | nightly-backup | done | low | `job-0553: nightly-backup -- done priority:low` |
| job-0142 | resize-images | running | low | `job-0142: resize-images -- running priority:low` |
| job-0686 | renew-certs | failed | low | `job-0686: renew-certs -- failed priority:low` |
| job-0018 | rotate-keys | done | low | `job-0018: rotate-keys -- done priority:low` |
| job-0787 | sync-inventory | pending | low | `job-0787: sync-inventory -- pending priority:low` |
| job-0347 | purge-cache | failed | normal | `job-0347: purge-cache -- failed priority:normal` |
| job-0626 | export-ledger | running | normal | `job-0626: export-ledger -- running priority:normal` |
| job-0721 | sync-inventory | running | low | `job-0721: sync-inventory -- running priority:low` |
| job-0715 | invoice-run | failed | normal | `job-0715: invoice-run -- failed priority:normal` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
