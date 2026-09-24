# Exec Summary view

Module: `views/exec_summary.py`. Audience: the platform team's wall display.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0416 | rotate-keys | running | high | `!!! job-0416: rotate-keys -- running` |
| job-0731 | sync-inventory | done | low | `! job-0731: sync-inventory -- done` |
| job-0265 | rotate-keys | failed | normal | `!! job-0265: rotate-keys -- failed` |
| job-0679 | sync-inventory | running | high | `!!! job-0679: sync-inventory -- running` |
| job-0757 | rebuild-feed | failed | low | `! job-0757: rebuild-feed -- failed` |
| job-0626 | reindex-search | pending | high | `!!! job-0626: reindex-search -- pending` |
| job-0632 | renew-certs | failed | low | `! job-0632: renew-certs -- failed` |
| job-0412 | rebuild-feed | running | normal | `!! job-0412: rebuild-feed -- running` |
| job-0609 | purge-cache | failed | normal | `!! job-0609: purge-cache -- failed` |
| job-0065 | reindex-search | failed | normal | `!! job-0065: reindex-search -- failed` |
| job-0323 | compact-logs | running | low | `! job-0323: compact-logs -- running` |
| job-0615 | nightly-backup | pending | low | `! job-0615: nightly-backup -- pending` |
| job-0280 | nightly-backup | failed | normal | `!! job-0280: nightly-backup -- failed` |
| job-0006 | compact-logs | done | low | `! job-0006: compact-logs -- done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
