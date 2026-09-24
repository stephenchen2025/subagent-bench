# Email Subject view

Module: `views/email_subject.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0849 | renew-certs | failed | normal | `renew-certs (job-0849) is failed --` |
| job-0352 | send-digest | done | normal | `send-digest (job-0352) is done --` |
| job-0380 | renew-certs | done | high | `renew-certs (job-0380) is done ^^` |
| job-0422 | purge-cache | done | high | `purge-cache (job-0422) is done ^^` |
| job-0552 | export-ledger | running | high | `export-ledger (job-0552) is running ^^` |
| job-0140 | reindex-search | failed | normal | `reindex-search (job-0140) is failed --` |
| job-0452 | compact-logs | failed | high | `compact-logs (job-0452) is failed ^^` |
| job-0274 | resize-images | done | normal | `resize-images (job-0274) is done --` |
| job-0462 | invoice-run | pending | high | `invoice-run (job-0462) is pending ^^` |
| job-0040 | renew-certs | running | high | `renew-certs (job-0040) is running ^^` |
| job-0070 | reindex-search | done | normal | `reindex-search (job-0070) is done --` |
| job-0020 | resize-images | done | normal | `resize-images (job-0020) is done --` |
| job-0233 | resize-images | pending | normal | `resize-images (job-0233) is pending --` |
| job-0662 | nightly-backup | pending | low | `nightly-backup (job-0662) is pending vv` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
