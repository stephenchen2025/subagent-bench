# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: auditors reviewing job history.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0602 | export-ledger | failed | normal | `export-ledger (job-0602) is failed **` |
| job-0539 | nightly-backup | failed | low | `nightly-backup (job-0539) is failed *` |
| job-0292 | invoice-run | pending | low | `invoice-run (job-0292) is pending *` |
| job-0148 | invoice-run | pending | high | `invoice-run (job-0148) is pending ***` |
| job-0627 | invoice-run | failed | high | `invoice-run (job-0627) is failed ***` |
| job-0581 | sync-inventory | failed | low | `sync-inventory (job-0581) is failed *` |
| job-0647 | sync-inventory | running | high | `sync-inventory (job-0647) is running ***` |
| job-0076 | reindex-search | running | normal | `reindex-search (job-0076) is running **` |
| job-0341 | invoice-run | done | high | `invoice-run (job-0341) is done ***` |
| job-0410 | export-ledger | running | low | `export-ledger (job-0410) is running *` |
| job-0854 | rotate-keys | running | low | `rotate-keys (job-0854) is running *` |
| job-0521 | invoice-run | done | low | `invoice-run (job-0521) is done *` |
| job-0464 | purge-cache | failed | low | `purge-cache (job-0464) is failed *` |
| job-0157 | export-ledger | done | low | `export-ledger (job-0157) is done *` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
