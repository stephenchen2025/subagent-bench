# Log Line view

Module: `views/log_line.py`. Audience: release managers.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0683 | invoice-run | running | normal | `level=2 job-0683 | invoice-run | running` |
| job-0455 | send-digest | pending | low | `level=1 job-0455 | send-digest | pending` |
| job-0869 | renew-certs | done | low | `level=1 job-0869 | renew-certs | done` |
| job-0234 | send-digest | done | high | `level=3 job-0234 | send-digest | done` |
| job-0501 | resize-images | done | normal | `level=2 job-0501 | resize-images | done` |
| job-0164 | export-ledger | running | normal | `level=2 job-0164 | export-ledger | running` |
| job-0191 | renew-certs | failed | normal | `level=2 job-0191 | renew-certs | failed` |
| job-0639 | reindex-search | failed | normal | `level=2 job-0639 | reindex-search | failed` |
| job-0307 | nightly-backup | running | normal | `level=2 job-0307 | nightly-backup | running` |
| job-0666 | rebuild-feed | failed | low | `level=1 job-0666 | rebuild-feed | failed` |
| job-0331 | reindex-search | running | normal | `level=2 job-0331 | reindex-search | running` |
| job-0648 | compact-logs | done | low | `level=1 job-0648 | compact-logs | done` |
| job-0845 | send-digest | pending | normal | `level=2 job-0845 | send-digest | pending` |
| job-0103 | export-ledger | pending | high | `level=3 job-0103 | export-ledger | pending` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
