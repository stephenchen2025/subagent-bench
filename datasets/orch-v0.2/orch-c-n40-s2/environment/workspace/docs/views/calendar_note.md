# Calendar Note view

Module: `views/calendar_note.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0546 | sync-inventory | failed | high | `job job-0546 / sync-inventory / failed level=3` |
| job-0930 | renew-certs | pending | low | `job job-0930 / renew-certs / pending level=1` |
| job-0264 | resize-images | failed | high | `job job-0264 / resize-images / failed level=3` |
| job-0028 | rotate-keys | done | high | `job job-0028 / rotate-keys / done level=3` |
| job-0140 | reindex-search | pending | high | `job job-0140 / reindex-search / pending level=3` |
| job-0836 | reindex-search | pending | low | `job job-0836 / reindex-search / pending level=1` |
| job-0739 | nightly-backup | pending | low | `job job-0739 / nightly-backup / pending level=1` |
| job-0463 | export-ledger | done | normal | `job job-0463 / export-ledger / done level=2` |
| job-0256 | rotate-keys | done | high | `job job-0256 / rotate-keys / done level=3` |
| job-0641 | purge-cache | pending | high | `job job-0641 / purge-cache / pending level=3` |
| job-0852 | compact-logs | done | high | `job job-0852 / compact-logs / done level=3` |
| job-0802 | compact-logs | failed | high | `job job-0802 / compact-logs / failed level=3` |
| job-0484 | send-digest | running | high | `job job-0484 / send-digest / running level=3` |
| job-0361 | compact-logs | running | low | `job job-0361 / compact-logs / running level=1` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
