# Audit Row view

Module: `views/audit_row.py`. Audience: release managers.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0893 | nightly-backup | pending | normal | `nightly-backup (job-0893) is pending color=amber` |
| job-0989 | purge-cache | pending | normal | `purge-cache (job-0989) is pending color=amber` |
| job-0290 | sync-inventory | done | low | `sync-inventory (job-0290) is done color=green` |
| job-0700 | nightly-backup | done | high | `nightly-backup (job-0700) is done color=red` |
| job-0670 | compact-logs | pending | normal | `compact-logs (job-0670) is pending color=amber` |
| job-0991 | invoice-run | running | normal | `invoice-run (job-0991) is running color=amber` |
| job-0619 | nightly-backup | failed | high | `nightly-backup (job-0619) is failed color=red` |
| job-0046 | rotate-keys | done | high | `rotate-keys (job-0046) is done color=red` |
| job-0963 | nightly-backup | failed | normal | `nightly-backup (job-0963) is failed color=amber` |
| job-0094 | rotate-keys | running | normal | `rotate-keys (job-0094) is running color=amber` |
| job-0392 | invoice-run | pending | low | `invoice-run (job-0392) is pending color=green` |
| job-0988 | invoice-run | running | high | `invoice-run (job-0988) is running color=red` |
| job-0305 | compact-logs | failed | low | `compact-logs (job-0305) is failed color=green` |
| job-0916 | sync-inventory | done | normal | `sync-inventory (job-0916) is done color=amber` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
