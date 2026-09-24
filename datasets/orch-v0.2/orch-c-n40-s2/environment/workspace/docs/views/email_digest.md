# Email Digest view

Module: `views/email_digest.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0468 | renew-certs | failed | normal | `renew-certs (job-0468) is failed **` |
| job-0526 | export-ledger | pending | high | `export-ledger (job-0526) is pending ***` |
| job-0920 | compact-logs | done | low | `compact-logs (job-0920) is done *` |
| job-0142 | renew-certs | running | normal | `renew-certs (job-0142) is running **` |
| job-0269 | resize-images | failed | high | `resize-images (job-0269) is failed ***` |
| job-0856 | export-ledger | running | high | `export-ledger (job-0856) is running ***` |
| job-0543 | resize-images | done | normal | `resize-images (job-0543) is done **` |
| job-0009 | send-digest | running | high | `send-digest (job-0009) is running ***` |
| job-0982 | compact-logs | done | normal | `compact-logs (job-0982) is done **` |
| job-0085 | resize-images | failed | high | `resize-images (job-0085) is failed ***` |
| job-0869 | purge-cache | failed | normal | `purge-cache (job-0869) is failed **` |
| job-0829 | reindex-search | running | low | `reindex-search (job-0829) is running *` |
| job-0388 | send-digest | failed | high | `send-digest (job-0388) is failed ***` |
| job-0595 | export-ledger | pending | normal | `export-ledger (job-0595) is pending **` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
