# Mobile Push view

Module: `views/mobile_push.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0153 | resize-images | running | normal | `P2 job job-0153 / resize-images / running` |
| job-0127 | export-ledger | running | low | `P3 job job-0127 / export-ledger / running` |
| job-0375 | compact-logs | done | low | `P3 job job-0375 / compact-logs / done` |
| job-0540 | rebuild-feed | pending | low | `P3 job job-0540 / rebuild-feed / pending` |
| job-0272 | renew-certs | failed | high | `P1 job job-0272 / renew-certs / failed` |
| job-0078 | renew-certs | failed | high | `P1 job job-0078 / renew-certs / failed` |
| job-0839 | reindex-search | failed | high | `P1 job job-0839 / reindex-search / failed` |
| job-0604 | compact-logs | done | normal | `P2 job job-0604 / compact-logs / done` |
| job-0077 | nightly-backup | running | normal | `P2 job job-0077 / nightly-backup / running` |
| job-0437 | rebuild-feed | running | normal | `P2 job job-0437 / rebuild-feed / running` |
| job-0436 | purge-cache | failed | high | `P1 job job-0436 / purge-cache / failed` |
| job-0589 | purge-cache | failed | low | `P3 job job-0589 / purge-cache / failed` |
| job-0809 | compact-logs | running | high | `P1 job job-0809 / compact-logs / running` |
| job-0777 | compact-logs | pending | low | `P3 job job-0777 / compact-logs / pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
