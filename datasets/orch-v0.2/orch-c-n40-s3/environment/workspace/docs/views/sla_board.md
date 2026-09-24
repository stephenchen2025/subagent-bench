# Sla Board view

Module: `views/sla_board.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0476 | resize-images | running | normal | `job-0476 | resize-images | running [NORMAL]` |
| job-0384 | compact-logs | pending | low | `job-0384 | compact-logs | pending [LOW]` |
| job-0176 | purge-cache | running | high | `job-0176 | purge-cache | running [HIGH]` |
| job-0933 | invoice-run | failed | low | `job-0933 | invoice-run | failed [LOW]` |
| job-0676 | rebuild-feed | done | high | `job-0676 | rebuild-feed | done [HIGH]` |
| job-0797 | reindex-search | done | low | `job-0797 | reindex-search | done [LOW]` |
| job-0533 | reindex-search | failed | normal | `job-0533 | reindex-search | failed [NORMAL]` |
| job-0548 | nightly-backup | done | normal | `job-0548 | nightly-backup | done [NORMAL]` |
| job-0658 | resize-images | failed | normal | `job-0658 | resize-images | failed [NORMAL]` |
| job-0462 | send-digest | failed | low | `job-0462 | send-digest | failed [LOW]` |
| job-0161 | reindex-search | running | normal | `job-0161 | reindex-search | running [NORMAL]` |
| job-0136 | send-digest | pending | normal | `job-0136 | send-digest | pending [NORMAL]` |
| job-0287 | rotate-keys | done | normal | `job-0287 | rotate-keys | done [NORMAL]` |
| job-0714 | reindex-search | pending | high | `job-0714 | reindex-search | pending [HIGH]` |

## History

- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
