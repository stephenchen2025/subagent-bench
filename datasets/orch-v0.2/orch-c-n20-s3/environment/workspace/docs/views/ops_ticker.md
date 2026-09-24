# Ops Ticker view

Module: `views/ops_ticker.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0536 | renew-certs | pending | high | `!!! job-0536 | renew-certs | pending` |
| job-0631 | rebuild-feed | done | high | `!!! job-0631 | rebuild-feed | done` |
| job-0882 | resize-images | pending | low | `! job-0882 | resize-images | pending` |
| job-0259 | send-digest | pending | high | `!!! job-0259 | send-digest | pending` |
| job-0166 | resize-images | done | low | `! job-0166 | resize-images | done` |
| job-0807 | purge-cache | failed | high | `!!! job-0807 | purge-cache | failed` |
| job-0618 | compact-logs | running | normal | `!! job-0618 | compact-logs | running` |
| job-0133 | reindex-search | pending | normal | `!! job-0133 | reindex-search | pending` |
| job-0104 | export-ledger | pending | low | `! job-0104 | export-ledger | pending` |
| job-0985 | rebuild-feed | pending | low | `! job-0985 | rebuild-feed | pending` |
| job-0007 | rotate-keys | pending | high | `!!! job-0007 | rotate-keys | pending` |
| job-0668 | reindex-search | failed | high | `!!! job-0668 | reindex-search | failed` |
| job-0253 | compact-logs | pending | high | `!!! job-0253 | compact-logs | pending` |
| job-0100 | compact-logs | pending | high | `!!! job-0100 | compact-logs | pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
