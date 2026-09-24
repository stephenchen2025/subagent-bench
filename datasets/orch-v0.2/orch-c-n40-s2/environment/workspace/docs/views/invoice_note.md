# Invoice Note view

Module: `views/invoice_note.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0810 | reindex-search | running | high | `RUNNING: reindex-search [job-0810] !!!` |
| job-0038 | purge-cache | pending | low | `PENDING: purge-cache [job-0038] !` |
| job-0657 | renew-certs | failed | high | `FAILED: renew-certs [job-0657] !!!` |
| job-0363 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0363] !!!` |
| job-0018 | invoice-run | done | low | `DONE: invoice-run [job-0018] !` |
| job-0280 | compact-logs | pending | low | `PENDING: compact-logs [job-0280] !` |
| job-0276 | export-ledger | failed | normal | `FAILED: export-ledger [job-0276] !!` |
| job-0245 | renew-certs | done | normal | `DONE: renew-certs [job-0245] !!` |
| job-0647 | compact-logs | failed | high | `FAILED: compact-logs [job-0647] !!!` |
| job-0089 | send-digest | running | high | `RUNNING: send-digest [job-0089] !!!` |
| job-0444 | purge-cache | running | normal | `RUNNING: purge-cache [job-0444] !!` |
| job-0598 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0598] !` |
| job-0216 | rotate-keys | pending | high | `PENDING: rotate-keys [job-0216] !!!` |
| job-0519 | rotate-keys | pending | low | `PENDING: rotate-keys [job-0519] !` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
