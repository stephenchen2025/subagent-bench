# Sla Board view

Module: `views/sla_board.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0692 | rotate-keys | running | normal | `RUNNING: rotate-keys [job-0692] color=amber` |
| job-0377 | send-digest | failed | normal | `FAILED: send-digest [job-0377] color=amber` |
| job-0173 | reindex-search | done | low | `DONE: reindex-search [job-0173] color=green` |
| job-0305 | renew-certs | pending | high | `PENDING: renew-certs [job-0305] color=red` |
| job-0793 | rotate-keys | pending | normal | `PENDING: rotate-keys [job-0793] color=amber` |
| job-0852 | invoice-run | pending | high | `PENDING: invoice-run [job-0852] color=red` |
| job-0316 | reindex-search | done | low | `DONE: reindex-search [job-0316] color=green` |
| job-0606 | send-digest | pending | low | `PENDING: send-digest [job-0606] color=green` |
| job-0851 | renew-certs | running | normal | `RUNNING: renew-certs [job-0851] color=amber` |
| job-0842 | export-ledger | running | low | `RUNNING: export-ledger [job-0842] color=green` |
| job-0997 | renew-certs | done | high | `DONE: renew-certs [job-0997] color=red` |
| job-0007 | compact-logs | running | normal | `RUNNING: compact-logs [job-0007] color=amber` |
| job-0763 | rebuild-feed | pending | low | `PENDING: rebuild-feed [job-0763] color=green` |
| job-0288 | nightly-backup | failed | high | `FAILED: nightly-backup [job-0288] color=red` |

## History

- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
