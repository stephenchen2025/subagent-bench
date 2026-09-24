# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: mobile users.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0059 | invoice-run | done | normal | `invoice-run (job-0059) is done level=2` |
| job-0641 | resize-images | pending | normal | `resize-images (job-0641) is pending level=2` |
| job-0194 | invoice-run | done | normal | `invoice-run (job-0194) is done level=2` |
| job-0508 | rotate-keys | pending | normal | `rotate-keys (job-0508) is pending level=2` |
| job-0919 | nightly-backup | failed | normal | `nightly-backup (job-0919) is failed level=2` |
| job-0372 | send-digest | done | low | `send-digest (job-0372) is done level=1` |
| job-0928 | rebuild-feed | done | high | `rebuild-feed (job-0928) is done level=3` |
| job-0172 | sync-inventory | done | low | `sync-inventory (job-0172) is done level=1` |
| job-0051 | compact-logs | done | high | `compact-logs (job-0051) is done level=3` |
| job-0955 | send-digest | done | low | `send-digest (job-0955) is done level=1` |
| job-0036 | sync-inventory | running | high | `sync-inventory (job-0036) is running level=3` |
| job-0101 | rotate-keys | running | normal | `rotate-keys (job-0101) is running level=2` |
| job-0588 | reindex-search | failed | high | `reindex-search (job-0588) is failed level=3` |
| job-0961 | rotate-keys | failed | low | `rotate-keys (job-0961) is failed level=1` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
