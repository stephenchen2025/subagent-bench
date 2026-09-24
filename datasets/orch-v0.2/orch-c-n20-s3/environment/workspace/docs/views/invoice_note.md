# Invoice Note view

Module: `views/invoice_note.py`. Audience: auditors reviewing job history.

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
| job-0297 | compact-logs | done | normal | `job job-0297 / compact-logs / done P2` |
| job-0587 | renew-certs | running | low | `job job-0587 / renew-certs / running P3` |
| job-0456 | resize-images | done | normal | `job job-0456 / resize-images / done P2` |
| job-0764 | purge-cache | done | normal | `job job-0764 / purge-cache / done P2` |
| job-0358 | reindex-search | running | normal | `job job-0358 / reindex-search / running P2` |
| job-0369 | rebuild-feed | done | low | `job job-0369 / rebuild-feed / done P3` |
| job-0698 | renew-certs | running | high | `job job-0698 / renew-certs / running P1` |
| job-0413 | reindex-search | failed | high | `job job-0413 / reindex-search / failed P1` |
| job-0755 | sync-inventory | done | normal | `job job-0755 / sync-inventory / done P2` |
| job-0904 | nightly-backup | pending | high | `job job-0904 / nightly-backup / pending P1` |
| job-0374 | nightly-backup | done | normal | `job job-0374 / nightly-backup / done P2` |
| job-0071 | compact-logs | failed | low | `job job-0071 / compact-logs / failed P3` |
| job-0781 | compact-logs | running | normal | `job job-0781 / compact-logs / running P2` |
| job-0303 | reindex-search | done | low | `job job-0303 / reindex-search / done P3` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
