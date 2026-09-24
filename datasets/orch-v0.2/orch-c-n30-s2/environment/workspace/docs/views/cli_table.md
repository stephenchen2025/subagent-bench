# Cli Table view

Module: `views/cli_table.py`. Audience: the finance team's weekly review.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0420 | renew-certs | done | low | `[LOW] DONE: renew-certs [job-0420]` |
| job-0559 | export-ledger | pending | high | `[HIGH] PENDING: export-ledger [job-0559]` |
| job-0371 | nightly-backup | done | low | `[LOW] DONE: nightly-backup [job-0371]` |
| job-0704 | reindex-search | done | low | `[LOW] DONE: reindex-search [job-0704]` |
| job-0532 | compact-logs | running | low | `[LOW] RUNNING: compact-logs [job-0532]` |
| job-0551 | export-ledger | running | normal | `[NORMAL] RUNNING: export-ledger [job-0551]` |
| job-0273 | send-digest | running | normal | `[NORMAL] RUNNING: send-digest [job-0273]` |
| job-0892 | rotate-keys | failed | high | `[HIGH] FAILED: rotate-keys [job-0892]` |
| job-0973 | sync-inventory | failed | high | `[HIGH] FAILED: sync-inventory [job-0973]` |
| job-0496 | rotate-keys | running | low | `[LOW] RUNNING: rotate-keys [job-0496]` |
| job-0175 | nightly-backup | pending | low | `[LOW] PENDING: nightly-backup [job-0175]` |
| job-0660 | invoice-run | pending | low | `[LOW] PENDING: invoice-run [job-0660]` |
| job-0104 | rotate-keys | done | normal | `[NORMAL] DONE: rotate-keys [job-0104]` |
| job-0298 | invoice-run | pending | high | `[HIGH] PENDING: invoice-run [job-0298]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
