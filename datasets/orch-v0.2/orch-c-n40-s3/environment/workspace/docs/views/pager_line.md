# Pager Line view

Module: `views/pager_line.py`. Audience: mobile users.

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
| job-0780 | compact-logs | running | normal | `level=2 RUNNING: compact-logs [job-0780]` |
| job-0992 | purge-cache | failed | high | `level=3 FAILED: purge-cache [job-0992]` |
| job-0288 | renew-certs | running | high | `level=3 RUNNING: renew-certs [job-0288]` |
| job-0143 | invoice-run | failed | high | `level=3 FAILED: invoice-run [job-0143]` |
| job-0799 | sync-inventory | done | low | `level=1 DONE: sync-inventory [job-0799]` |
| job-0631 | purge-cache | failed | normal | `level=2 FAILED: purge-cache [job-0631]` |
| job-0239 | reindex-search | running | low | `level=1 RUNNING: reindex-search [job-0239]` |
| job-0729 | resize-images | done | low | `level=1 DONE: resize-images [job-0729]` |
| job-0165 | renew-certs | pending | low | `level=1 PENDING: renew-certs [job-0165]` |
| job-0228 | sync-inventory | done | normal | `level=2 DONE: sync-inventory [job-0228]` |
| job-0183 | invoice-run | running | high | `level=3 RUNNING: invoice-run [job-0183]` |
| job-0932 | nightly-backup | done | low | `level=1 DONE: nightly-backup [job-0932]` |
| job-0706 | rebuild-feed | done | high | `level=3 DONE: rebuild-feed [job-0706]` |
| job-0888 | resize-images | pending | normal | `level=2 PENDING: resize-images [job-0888]` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
