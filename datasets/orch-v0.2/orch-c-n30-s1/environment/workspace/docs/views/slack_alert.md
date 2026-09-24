# Slack Alert view

Module: `views/slack_alert.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0267 | sync-inventory | pending | high | `[HIGH] job job-0267 / sync-inventory / pending` |
| job-0623 | rotate-keys | running | high | `[HIGH] job job-0623 / rotate-keys / running` |
| job-0330 | reindex-search | pending | high | `[HIGH] job job-0330 / reindex-search / pending` |
| job-0778 | compact-logs | done | normal | `[NORMAL] job job-0778 / compact-logs / done` |
| job-0463 | reindex-search | done | low | `[LOW] job job-0463 / reindex-search / done` |
| job-0681 | reindex-search | done | low | `[LOW] job job-0681 / reindex-search / done` |
| job-0934 | send-digest | running | high | `[HIGH] job job-0934 / send-digest / running` |
| job-0214 | invoice-run | pending | low | `[LOW] job job-0214 / invoice-run / pending` |
| job-0114 | export-ledger | pending | normal | `[NORMAL] job job-0114 / export-ledger / pending` |
| job-0161 | send-digest | running | normal | `[NORMAL] job job-0161 / send-digest / running` |
| job-0461 | renew-certs | done | high | `[HIGH] job job-0461 / renew-certs / done` |
| job-0766 | sync-inventory | done | low | `[LOW] job job-0766 / sync-inventory / done` |
| job-0036 | nightly-backup | running | low | `[LOW] job job-0036 / nightly-backup / running` |
| job-0428 | purge-cache | running | low | `[LOW] job job-0428 / purge-cache / running` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
