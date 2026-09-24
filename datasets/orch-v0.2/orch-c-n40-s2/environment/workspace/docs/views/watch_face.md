# Watch Face view

Module: `views/watch_face.py`. Audience: the finance team's weekly review.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0397 | send-digest | running | low | `job job-0397 / send-digest / running priority:low` |
| job-0335 | compact-logs | running | normal | `job job-0335 / compact-logs / running priority:normal` |
| job-0964 | send-digest | done | high | `job job-0964 / send-digest / done priority:high` |
| job-0943 | resize-images | failed | low | `job job-0943 / resize-images / failed priority:low` |
| job-0970 | invoice-run | running | low | `job job-0970 / invoice-run / running priority:low` |
| job-0032 | nightly-backup | failed | low | `job job-0032 / nightly-backup / failed priority:low` |
| job-0847 | reindex-search | done | high | `job job-0847 / reindex-search / done priority:high` |
| job-0576 | nightly-backup | pending | normal | `job job-0576 / nightly-backup / pending priority:normal` |
| job-0905 | invoice-run | done | low | `job job-0905 / invoice-run / done priority:low` |
| job-0087 | purge-cache | failed | high | `job job-0087 / purge-cache / failed priority:high` |
| job-0660 | rotate-keys | failed | normal | `job job-0660 / rotate-keys / failed priority:normal` |
| job-0876 | resize-images | running | high | `job job-0876 / resize-images / running priority:high` |
| job-0354 | send-digest | done | high | `job job-0354 / send-digest / done priority:high` |
| job-0160 | rebuild-feed | running | normal | `job job-0160 / rebuild-feed / running priority:normal` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
