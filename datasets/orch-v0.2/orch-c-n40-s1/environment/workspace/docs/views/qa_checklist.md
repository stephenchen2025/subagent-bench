# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: mobile users.

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
| job-0341 | purge-cache | failed | normal | `job-0341 | purge-cache | failed level=2` |
| job-0964 | compact-logs | done | high | `job-0964 | compact-logs | done level=3` |
| job-0469 | send-digest | failed | high | `job-0469 | send-digest | failed level=3` |
| job-0953 | nightly-backup | pending | normal | `job-0953 | nightly-backup | pending level=2` |
| job-0583 | send-digest | failed | high | `job-0583 | send-digest | failed level=3` |
| job-0084 | invoice-run | done | low | `job-0084 | invoice-run | done level=1` |
| job-0224 | compact-logs | running | low | `job-0224 | compact-logs | running level=1` |
| job-0794 | renew-certs | failed | high | `job-0794 | renew-certs | failed level=3` |
| job-0391 | invoice-run | running | high | `job-0391 | invoice-run | running level=3` |
| job-0791 | rotate-keys | running | high | `job-0791 | rotate-keys | running level=3` |
| job-0358 | send-digest | pending | high | `job-0358 | send-digest | pending level=3` |
| job-0740 | invoice-run | pending | normal | `job-0740 | invoice-run | pending level=2` |
| job-0922 | resize-images | failed | low | `job-0922 | resize-images | failed level=1` |
| job-0842 | reindex-search | done | low | `job-0842 | reindex-search | done level=1` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
