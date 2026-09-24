# Slack Alert view

Module: `views/slack_alert.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0679 | reindex-search | running | high | `color=red job job-0679 / reindex-search / running` |
| job-0482 | invoice-run | failed | low | `color=green job job-0482 / invoice-run / failed` |
| job-0852 | rotate-keys | running | high | `color=red job job-0852 / rotate-keys / running` |
| job-0256 | sync-inventory | pending | low | `color=green job job-0256 / sync-inventory / pending` |
| job-0589 | nightly-backup | done | normal | `color=amber job job-0589 / nightly-backup / done` |
| job-0247 | rebuild-feed | running | normal | `color=amber job job-0247 / rebuild-feed / running` |
| job-0013 | rotate-keys | running | low | `color=green job job-0013 / rotate-keys / running` |
| job-0297 | renew-certs | failed | low | `color=green job job-0297 / renew-certs / failed` |
| job-0024 | compact-logs | running | low | `color=green job job-0024 / compact-logs / running` |
| job-0546 | reindex-search | pending | high | `color=red job job-0546 / reindex-search / pending` |
| job-0023 | send-digest | failed | normal | `color=amber job job-0023 / send-digest / failed` |
| job-0373 | invoice-run | pending | high | `color=red job job-0373 / invoice-run / pending` |
| job-0443 | reindex-search | pending | high | `color=red job job-0443 / reindex-search / pending` |
| job-0423 | export-ledger | done | high | `color=red job job-0423 / export-ledger / done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
