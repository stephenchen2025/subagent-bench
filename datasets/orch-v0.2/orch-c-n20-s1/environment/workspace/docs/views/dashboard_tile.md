# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: mobile users.

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
| job-0847 | export-ledger | pending | high | `job-0847: export-ledger -- pending ***` |
| job-0627 | export-ledger | done | low | `job-0627: export-ledger -- done *` |
| job-0752 | send-digest | pending | low | `job-0752: send-digest -- pending *` |
| job-0653 | rotate-keys | pending | normal | `job-0653: rotate-keys -- pending **` |
| job-0712 | reindex-search | failed | high | `job-0712: reindex-search -- failed ***` |
| job-0618 | nightly-backup | done | low | `job-0618: nightly-backup -- done *` |
| job-0828 | nightly-backup | pending | normal | `job-0828: nightly-backup -- pending **` |
| job-0092 | renew-certs | pending | normal | `job-0092: renew-certs -- pending **` |
| job-0842 | rotate-keys | failed | normal | `job-0842: rotate-keys -- failed **` |
| job-0066 | send-digest | done | high | `job-0066: send-digest -- done ***` |
| job-0897 | renew-certs | failed | low | `job-0897: renew-certs -- failed *` |
| job-0798 | rebuild-feed | running | normal | `job-0798: rebuild-feed -- running **` |
| job-0666 | compact-logs | done | normal | `job-0666: compact-logs -- done **` |
| job-0383 | rebuild-feed | failed | low | `job-0383: rebuild-feed -- failed *` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
