# Teams Card view

Module: `views/teams_card.py`. Audience: the finance team's weekly review.

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
| job-0914 | nightly-backup | running | high | `job job-0914 / nightly-backup / running level=3` |
| job-0317 | renew-certs | running | normal | `job job-0317 / renew-certs / running level=2` |
| job-0551 | invoice-run | running | high | `job job-0551 / invoice-run / running level=3` |
| job-0462 | export-ledger | done | high | `job job-0462 / export-ledger / done level=3` |
| job-0681 | export-ledger | pending | normal | `job job-0681 / export-ledger / pending level=2` |
| job-0451 | resize-images | done | high | `job job-0451 / resize-images / done level=3` |
| job-0804 | nightly-backup | failed | normal | `job job-0804 / nightly-backup / failed level=2` |
| job-0889 | renew-certs | failed | normal | `job job-0889 / renew-certs / failed level=2` |
| job-0275 | invoice-run | running | normal | `job job-0275 / invoice-run / running level=2` |
| job-0113 | export-ledger | pending | high | `job job-0113 / export-ledger / pending level=3` |
| job-0347 | export-ledger | failed | low | `job job-0347 / export-ledger / failed level=1` |
| job-0412 | renew-certs | done | low | `job job-0412 / renew-certs / done level=1` |
| job-0059 | purge-cache | failed | low | `job job-0059 / purge-cache / failed level=1` |
| job-0596 | send-digest | running | low | `job job-0596 / send-digest / running level=1` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
