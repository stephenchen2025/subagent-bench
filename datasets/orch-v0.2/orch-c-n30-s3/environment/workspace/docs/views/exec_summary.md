# Exec Summary view

Module: `views/exec_summary.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0352 | nightly-backup | running | high | `job-0352 | nightly-backup | running P1` |
| job-0306 | compact-logs | failed | high | `job-0306 | compact-logs | failed P1` |
| job-0527 | nightly-backup | pending | low | `job-0527 | nightly-backup | pending P3` |
| job-0341 | compact-logs | done | normal | `job-0341 | compact-logs | done P2` |
| job-0673 | rotate-keys | done | normal | `job-0673 | rotate-keys | done P2` |
| job-0359 | rotate-keys | failed | low | `job-0359 | rotate-keys | failed P3` |
| job-0378 | renew-certs | done | high | `job-0378 | renew-certs | done P1` |
| job-0027 | rebuild-feed | done | low | `job-0027 | rebuild-feed | done P3` |
| job-0498 | export-ledger | running | normal | `job-0498 | export-ledger | running P2` |
| job-0355 | send-digest | pending | normal | `job-0355 | send-digest | pending P2` |
| job-0239 | rebuild-feed | running | high | `job-0239 | rebuild-feed | running P1` |
| job-0740 | export-ledger | running | low | `job-0740 | export-ledger | running P3` |
| job-0409 | purge-cache | pending | low | `job-0409 | purge-cache | pending P3` |
| job-0424 | rotate-keys | pending | normal | `job-0424 | rotate-keys | pending P2` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
