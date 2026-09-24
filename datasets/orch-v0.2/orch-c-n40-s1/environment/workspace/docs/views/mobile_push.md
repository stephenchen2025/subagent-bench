# Mobile Push view

Module: `views/mobile_push.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0597 | renew-certs | pending | high | `job-0597 | renew-certs | pending color=red` |
| job-0385 | sync-inventory | pending | high | `job-0385 | sync-inventory | pending color=red` |
| job-0873 | invoice-run | pending | high | `job-0873 | invoice-run | pending color=red` |
| job-0459 | resize-images | failed | low | `job-0459 | resize-images | failed color=green` |
| job-0411 | purge-cache | running | high | `job-0411 | purge-cache | running color=red` |
| job-0643 | export-ledger | failed | low | `job-0643 | export-ledger | failed color=green` |
| job-0630 | resize-images | pending | high | `job-0630 | resize-images | pending color=red` |
| job-0466 | purge-cache | running | normal | `job-0466 | purge-cache | running color=amber` |
| job-0931 | rotate-keys | running | low | `job-0931 | rotate-keys | running color=green` |
| job-0993 | resize-images | failed | low | `job-0993 | resize-images | failed color=green` |
| job-0291 | renew-certs | failed | high | `job-0291 | renew-certs | failed color=red` |
| job-0316 | renew-certs | done | normal | `job-0316 | renew-certs | done color=amber` |
| job-0727 | export-ledger | running | low | `job-0727 | export-ledger | running color=green` |
| job-0172 | export-ledger | pending | normal | `job-0172 | export-ledger | pending color=amber` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
