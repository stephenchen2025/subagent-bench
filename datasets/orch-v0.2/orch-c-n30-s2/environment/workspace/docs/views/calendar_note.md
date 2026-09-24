# Calendar Note view

Module: `views/calendar_note.py`. Audience: auditors reviewing job history.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0702 | export-ledger | failed | high | `job job-0702 / export-ledger / failed URGENT` |
| job-0679 | export-ledger | pending | high | `job job-0679 / export-ledger / pending URGENT` |
| job-0821 | sync-inventory | running | low | `job job-0821 / sync-inventory / running DEFERRABLE` |
| job-0079 | purge-cache | running | low | `job job-0079 / purge-cache / running DEFERRABLE` |
| job-0271 | export-ledger | pending | normal | `job job-0271 / export-ledger / pending ROUTINE` |
| job-0284 | invoice-run | failed | high | `job job-0284 / invoice-run / failed URGENT` |
| job-0644 | export-ledger | failed | low | `job job-0644 / export-ledger / failed DEFERRABLE` |
| job-0048 | export-ledger | failed | normal | `job job-0048 / export-ledger / failed ROUTINE` |
| job-0470 | nightly-backup | failed | high | `job job-0470 / nightly-backup / failed URGENT` |
| job-0882 | rebuild-feed | done | low | `job job-0882 / rebuild-feed / done DEFERRABLE` |
| job-0237 | reindex-search | failed | high | `job job-0237 / reindex-search / failed URGENT` |
| job-0928 | rotate-keys | running | low | `job job-0928 / rotate-keys / running DEFERRABLE` |
| job-0367 | send-digest | running | low | `job job-0367 / send-digest / running DEFERRABLE` |
| job-0257 | rotate-keys | failed | high | `job job-0257 / rotate-keys / failed URGENT` |

## History

- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
