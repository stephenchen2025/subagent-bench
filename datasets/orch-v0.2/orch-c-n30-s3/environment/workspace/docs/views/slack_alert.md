# Slack Alert view

Module: `views/slack_alert.py`. Audience: customer support leads.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0804 | compact-logs | done | low | `level=1 job job-0804 / compact-logs / done` |
| job-0506 | reindex-search | failed | normal | `level=2 job job-0506 / reindex-search / failed` |
| job-0774 | resize-images | failed | high | `level=3 job job-0774 / resize-images / failed` |
| job-0395 | resize-images | pending | high | `level=3 job job-0395 / resize-images / pending` |
| job-0595 | invoice-run | running | high | `level=3 job job-0595 / invoice-run / running` |
| job-0147 | invoice-run | done | normal | `level=2 job job-0147 / invoice-run / done` |
| job-0803 | nightly-backup | done | low | `level=1 job job-0803 / nightly-backup / done` |
| job-0295 | nightly-backup | pending | low | `level=1 job job-0295 / nightly-backup / pending` |
| job-0158 | export-ledger | failed | normal | `level=2 job job-0158 / export-ledger / failed` |
| job-0639 | compact-logs | failed | high | `level=3 job job-0639 / compact-logs / failed` |
| job-0627 | sync-inventory | done | low | `level=1 job job-0627 / sync-inventory / done` |
| job-0970 | nightly-backup | running | normal | `level=2 job job-0970 / nightly-backup / running` |
| job-0816 | purge-cache | done | high | `level=3 job job-0816 / purge-cache / done` |
| job-0427 | rotate-keys | running | low | `level=1 job job-0427 / rotate-keys / running` |

## History

- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
