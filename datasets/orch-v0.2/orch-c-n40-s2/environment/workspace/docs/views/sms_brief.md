# Sms Brief view

Module: `views/sms_brief.py`. Audience: customer support leads.

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
| job-0044 | resize-images | failed | normal | `P2 job job-0044 / resize-images / failed` |
| job-0580 | invoice-run | running | normal | `P2 job job-0580 / invoice-run / running` |
| job-0940 | renew-certs | running | low | `P3 job job-0940 / renew-certs / running` |
| job-0193 | rebuild-feed | failed | high | `P1 job job-0193 / rebuild-feed / failed` |
| job-0146 | renew-certs | failed | low | `P3 job job-0146 / renew-certs / failed` |
| job-0355 | resize-images | failed | high | `P1 job job-0355 / resize-images / failed` |
| job-0743 | purge-cache | done | low | `P3 job job-0743 / purge-cache / done` |
| job-0183 | nightly-backup | done | high | `P1 job job-0183 / nightly-backup / done` |
| job-0936 | invoice-run | pending | low | `P3 job job-0936 / invoice-run / pending` |
| job-0294 | rebuild-feed | running | high | `P1 job job-0294 / rebuild-feed / running` |
| job-0936 | resize-images | failed | high | `P1 job job-0936 / resize-images / failed` |
| job-0173 | compact-logs | done | low | `P3 job job-0173 / compact-logs / done` |
| job-0314 | export-ledger | pending | low | `P3 job job-0314 / export-ledger / pending` |
| job-0477 | invoice-run | done | normal | `P2 job job-0477 / invoice-run / done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
