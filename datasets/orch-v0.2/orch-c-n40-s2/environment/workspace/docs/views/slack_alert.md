# Slack Alert view

Module: `views/slack_alert.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0475 | send-digest | failed | high | `^^ job-0475: send-digest -- failed` |
| job-0224 | rebuild-feed | pending | high | `^^ job-0224: rebuild-feed -- pending` |
| job-0990 | rebuild-feed | pending | normal | `-- job-0990: rebuild-feed -- pending` |
| job-0234 | nightly-backup | done | normal | `-- job-0234: nightly-backup -- done` |
| job-0254 | export-ledger | running | low | `vv job-0254: export-ledger -- running` |
| job-0162 | reindex-search | done | high | `^^ job-0162: reindex-search -- done` |
| job-0530 | renew-certs | running | low | `vv job-0530: renew-certs -- running` |
| job-0107 | nightly-backup | failed | normal | `-- job-0107: nightly-backup -- failed` |
| job-0644 | invoice-run | done | high | `^^ job-0644: invoice-run -- done` |
| job-0654 | export-ledger | done | low | `vv job-0654: export-ledger -- done` |
| job-0281 | send-digest | failed | high | `^^ job-0281: send-digest -- failed` |
| job-0689 | invoice-run | running | normal | `-- job-0689: invoice-run -- running` |
| job-0520 | rebuild-feed | running | low | `vv job-0520: rebuild-feed -- running` |
| job-0771 | resize-images | failed | normal | `-- job-0771: resize-images -- failed` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
