# Sms Brief view

Module: `views/sms_brief.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0372 | rebuild-feed | done | high | `level=3 job job-0372 / rebuild-feed / done` |
| job-0718 | send-digest | running | normal | `level=2 job job-0718 / send-digest / running` |
| job-0926 | nightly-backup | pending | high | `level=3 job job-0926 / nightly-backup / pending` |
| job-0695 | renew-certs | running | high | `level=3 job job-0695 / renew-certs / running` |
| job-0347 | purge-cache | running | normal | `level=2 job job-0347 / purge-cache / running` |
| job-0700 | reindex-search | failed | normal | `level=2 job job-0700 / reindex-search / failed` |
| job-0838 | export-ledger | pending | high | `level=3 job job-0838 / export-ledger / pending` |
| job-0577 | rebuild-feed | failed | normal | `level=2 job job-0577 / rebuild-feed / failed` |
| job-0320 | invoice-run | running | normal | `level=2 job job-0320 / invoice-run / running` |
| job-0216 | nightly-backup | done | low | `level=1 job job-0216 / nightly-backup / done` |
| job-0860 | nightly-backup | failed | high | `level=3 job job-0860 / nightly-backup / failed` |
| job-0930 | nightly-backup | failed | high | `level=3 job job-0930 / nightly-backup / failed` |
| job-0233 | rebuild-feed | failed | high | `level=3 job job-0233 / rebuild-feed / failed` |
| job-0162 | purge-cache | pending | high | `level=3 job job-0162 / purge-cache / pending` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
