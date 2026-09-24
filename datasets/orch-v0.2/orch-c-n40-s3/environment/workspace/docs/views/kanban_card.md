# Kanban Card view

Module: `views/kanban_card.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0264 | rotate-keys | running | normal | `job job-0264 / rotate-keys / running P2` |
| job-0762 | compact-logs | running | high | `job job-0762 / compact-logs / running P1` |
| job-0461 | rotate-keys | pending | high | `job job-0461 / rotate-keys / pending P1` |
| job-0165 | rotate-keys | running | low | `job job-0165 / rotate-keys / running P3` |
| job-0943 | nightly-backup | running | low | `job job-0943 / nightly-backup / running P3` |
| job-0858 | reindex-search | failed | low | `job job-0858 / reindex-search / failed P3` |
| job-0184 | send-digest | pending | high | `job job-0184 / send-digest / pending P1` |
| job-0742 | renew-certs | failed | normal | `job job-0742 / renew-certs / failed P2` |
| job-0792 | reindex-search | running | normal | `job job-0792 / reindex-search / running P2` |
| job-0366 | purge-cache | failed | high | `job job-0366 / purge-cache / failed P1` |
| job-0809 | compact-logs | running | low | `job job-0809 / compact-logs / running P3` |
| job-0881 | resize-images | pending | high | `job job-0881 / resize-images / pending P1` |
| job-0495 | sync-inventory | pending | low | `job job-0495 / sync-inventory / pending P3` |
| job-0871 | invoice-run | pending | low | `job job-0871 / invoice-run / pending P3` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
