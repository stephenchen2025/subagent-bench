# Archive Label view

Module: `views/archive_label.py`. Audience: the executive summary email.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0559 | export-ledger | failed | high | `job-0559: export-ledger -- failed color=red` |
| job-0340 | nightly-backup | running | low | `job-0340: nightly-backup -- running color=green` |
| job-0657 | nightly-backup | failed | normal | `job-0657: nightly-backup -- failed color=amber` |
| job-0214 | rotate-keys | pending | low | `job-0214: rotate-keys -- pending color=green` |
| job-0423 | reindex-search | done | low | `job-0423: reindex-search -- done color=green` |
| job-0486 | renew-certs | failed | high | `job-0486: renew-certs -- failed color=red` |
| job-0946 | rotate-keys | pending | low | `job-0946: rotate-keys -- pending color=green` |
| job-0412 | nightly-backup | done | low | `job-0412: nightly-backup -- done color=green` |
| job-0347 | reindex-search | running | low | `job-0347: reindex-search -- running color=green` |
| job-0733 | send-digest | done | normal | `job-0733: send-digest -- done color=amber` |
| job-0589 | nightly-backup | running | normal | `job-0589: nightly-backup -- running color=amber` |
| job-0471 | rebuild-feed | failed | normal | `job-0471: rebuild-feed -- failed color=amber` |
| job-0220 | send-digest | pending | high | `job-0220: send-digest -- pending color=red` |
| job-0694 | rebuild-feed | done | low | `job-0694: rebuild-feed -- done color=green` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
