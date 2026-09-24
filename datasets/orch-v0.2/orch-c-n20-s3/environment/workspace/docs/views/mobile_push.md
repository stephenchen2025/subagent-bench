# Mobile Push view

Module: `views/mobile_push.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0084 | sync-inventory | pending | high | `job-0084 | sync-inventory | pending ^^` |
| job-0619 | compact-logs | done | normal | `job-0619 | compact-logs | done --` |
| job-0840 | renew-certs | running | normal | `job-0840 | renew-certs | running --` |
| job-0958 | rebuild-feed | running | low | `job-0958 | rebuild-feed | running vv` |
| job-0211 | sync-inventory | pending | low | `job-0211 | sync-inventory | pending vv` |
| job-0250 | purge-cache | running | low | `job-0250 | purge-cache | running vv` |
| job-0696 | rebuild-feed | running | low | `job-0696 | rebuild-feed | running vv` |
| job-0303 | invoice-run | pending | normal | `job-0303 | invoice-run | pending --` |
| job-0121 | rebuild-feed | running | normal | `job-0121 | rebuild-feed | running --` |
| job-0112 | rebuild-feed | done | high | `job-0112 | rebuild-feed | done ^^` |
| job-0257 | invoice-run | done | high | `job-0257 | invoice-run | done ^^` |
| job-0133 | send-digest | failed | normal | `job-0133 | send-digest | failed --` |
| job-0048 | renew-certs | done | high | `job-0048 | renew-certs | done ^^` |
| job-0439 | resize-images | failed | low | `job-0439 | resize-images | failed vv` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
