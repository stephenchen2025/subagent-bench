# Slack Alert view

Module: `views/slack_alert.py`. Audience: release managers.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0025 | nightly-backup | running | low | `RUNNING: nightly-backup [job-0025] vv` |
| job-0516 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0516] ^^` |
| job-0633 | send-digest | done | high | `DONE: send-digest [job-0633] ^^` |
| job-0127 | rotate-keys | done | low | `DONE: rotate-keys [job-0127] vv` |
| job-0771 | export-ledger | pending | low | `PENDING: export-ledger [job-0771] vv` |
| job-0779 | resize-images | running | low | `RUNNING: resize-images [job-0779] vv` |
| job-0611 | compact-logs | pending | low | `PENDING: compact-logs [job-0611] vv` |
| job-0100 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0100] ^^` |
| job-0792 | purge-cache | running | low | `RUNNING: purge-cache [job-0792] vv` |
| job-0926 | invoice-run | pending | normal | `PENDING: invoice-run [job-0926] --` |
| job-0347 | resize-images | pending | high | `PENDING: resize-images [job-0347] ^^` |
| job-0122 | rotate-keys | running | high | `RUNNING: rotate-keys [job-0122] ^^` |
| job-0870 | purge-cache | done | high | `DONE: purge-cache [job-0870] ^^` |
| job-0482 | sync-inventory | running | low | `RUNNING: sync-inventory [job-0482] vv` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
