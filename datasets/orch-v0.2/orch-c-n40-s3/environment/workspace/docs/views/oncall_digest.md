# Oncall Digest view

Module: `views/oncall_digest.py`. Audience: the on-call engineer who is paged at night.

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
| job-0929 | sync-inventory | done | low | `DONE: sync-inventory [job-0929] color=green` |
| job-0974 | compact-logs | pending | high | `PENDING: compact-logs [job-0974] color=red` |
| job-0851 | rebuild-feed | pending | normal | `PENDING: rebuild-feed [job-0851] color=amber` |
| job-0510 | sync-inventory | running | normal | `RUNNING: sync-inventory [job-0510] color=amber` |
| job-0421 | sync-inventory | running | high | `RUNNING: sync-inventory [job-0421] color=red` |
| job-0831 | resize-images | running | high | `RUNNING: resize-images [job-0831] color=red` |
| job-0702 | resize-images | pending | high | `PENDING: resize-images [job-0702] color=red` |
| job-0192 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0192] color=red` |
| job-0748 | send-digest | running | low | `RUNNING: send-digest [job-0748] color=green` |
| job-0209 | compact-logs | pending | low | `PENDING: compact-logs [job-0209] color=green` |
| job-0026 | rotate-keys | pending | normal | `PENDING: rotate-keys [job-0026] color=amber` |
| job-0573 | rotate-keys | done | low | `DONE: rotate-keys [job-0573] color=green` |
| job-0407 | invoice-run | pending | high | `PENDING: invoice-run [job-0407] color=red` |
| job-0261 | renew-certs | running | high | `RUNNING: renew-certs [job-0261] color=red` |

## History

- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
