# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0850 | nightly-backup | done | low | `level=1 DONE: nightly-backup [job-0850]` |
| job-0706 | export-ledger | pending | normal | `level=2 PENDING: export-ledger [job-0706]` |
| job-0089 | resize-images | done | low | `level=1 DONE: resize-images [job-0089]` |
| job-0446 | nightly-backup | failed | normal | `level=2 FAILED: nightly-backup [job-0446]` |
| job-0996 | renew-certs | done | high | `level=3 DONE: renew-certs [job-0996]` |
| job-0661 | export-ledger | pending | high | `level=3 PENDING: export-ledger [job-0661]` |
| job-0906 | export-ledger | failed | normal | `level=2 FAILED: export-ledger [job-0906]` |
| job-0184 | renew-certs | done | high | `level=3 DONE: renew-certs [job-0184]` |
| job-0212 | reindex-search | running | low | `level=1 RUNNING: reindex-search [job-0212]` |
| job-0489 | compact-logs | running | normal | `level=2 RUNNING: compact-logs [job-0489]` |
| job-0874 | rotate-keys | done | normal | `level=2 DONE: rotate-keys [job-0874]` |
| job-0066 | invoice-run | pending | low | `level=1 PENDING: invoice-run [job-0066]` |
| job-0895 | export-ledger | done | normal | `level=2 DONE: export-ledger [job-0895]` |
| job-0298 | purge-cache | failed | low | `level=1 FAILED: purge-cache [job-0298]` |

## History

- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
