# Status Badge view

Module: `views/status_badge.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0768 | send-digest | failed | normal | `job-0768 | send-digest | failed level=2` |
| job-0975 | reindex-search | done | high | `job-0975 | reindex-search | done level=3` |
| job-0028 | invoice-run | done | normal | `job-0028 | invoice-run | done level=2` |
| job-0214 | purge-cache | running | normal | `job-0214 | purge-cache | running level=2` |
| job-0271 | purge-cache | running | normal | `job-0271 | purge-cache | running level=2` |
| job-0088 | reindex-search | running | normal | `job-0088 | reindex-search | running level=2` |
| job-0798 | invoice-run | running | low | `job-0798 | invoice-run | running level=1` |
| job-0338 | resize-images | done | high | `job-0338 | resize-images | done level=3` |
| job-0875 | export-ledger | done | normal | `job-0875 | export-ledger | done level=2` |
| job-0161 | resize-images | done | normal | `job-0161 | resize-images | done level=2` |
| job-0361 | nightly-backup | done | normal | `job-0361 | nightly-backup | done level=2` |
| job-0224 | compact-logs | pending | normal | `job-0224 | compact-logs | pending level=2` |
| job-0029 | resize-images | failed | low | `job-0029 | resize-images | failed level=1` |
| job-0153 | renew-certs | done | high | `job-0153 | renew-certs | done level=3` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
