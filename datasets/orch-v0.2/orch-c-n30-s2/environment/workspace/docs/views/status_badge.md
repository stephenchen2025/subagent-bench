# Status Badge view

Module: `views/status_badge.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `level=3` |
| normal | `level=2` |
| low | `level=1` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0268 | send-digest | failed | low | `job job-0268 / send-digest / failed level=1` |
| job-0038 | purge-cache | pending | normal | `job job-0038 / purge-cache / pending level=2` |
| job-0702 | compact-logs | failed | normal | `job job-0702 / compact-logs / failed level=2` |
| job-0507 | rebuild-feed | done | normal | `job job-0507 / rebuild-feed / done level=2` |
| job-0294 | compact-logs | failed | high | `job job-0294 / compact-logs / failed level=3` |
| job-0100 | rebuild-feed | failed | low | `job job-0100 / rebuild-feed / failed level=1` |
| job-0458 | resize-images | running | high | `job job-0458 / resize-images / running level=3` |
| job-0656 | rebuild-feed | done | low | `job job-0656 / rebuild-feed / done level=1` |
| job-0876 | purge-cache | failed | normal | `job job-0876 / purge-cache / failed level=2` |
| job-0442 | rotate-keys | failed | normal | `job job-0442 / rotate-keys / failed level=2` |
| job-0450 | nightly-backup | failed | normal | `job job-0450 / nightly-backup / failed level=2` |
| job-0499 | sync-inventory | pending | normal | `job job-0499 / sync-inventory / pending level=2` |
| job-0139 | renew-certs | failed | low | `job job-0139 / renew-certs / failed level=1` |
| job-0834 | export-ledger | done | high | `job job-0834 / export-ledger / done level=3` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
