# Dashboard Tile view

Module: `views/dashboard_tile.py`. Audience: mobile users.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0639 | invoice-run | failed | high | `invoice-run (job-0639) is failed level=3` |
| job-0046 | purge-cache | pending | low | `purge-cache (job-0046) is pending level=1` |
| job-0480 | nightly-backup | failed | low | `nightly-backup (job-0480) is failed level=1` |
| job-0267 | invoice-run | running | low | `invoice-run (job-0267) is running level=1` |
| job-0755 | rotate-keys | pending | normal | `rotate-keys (job-0755) is pending level=2` |
| job-0730 | rebuild-feed | running | low | `rebuild-feed (job-0730) is running level=1` |
| job-0123 | sync-inventory | running | high | `sync-inventory (job-0123) is running level=3` |
| job-0894 | send-digest | failed | low | `send-digest (job-0894) is failed level=1` |
| job-0657 | invoice-run | running | low | `invoice-run (job-0657) is running level=1` |
| job-0923 | nightly-backup | done | normal | `nightly-backup (job-0923) is done level=2` |
| job-0939 | renew-certs | done | high | `renew-certs (job-0939) is done level=3` |
| job-0489 | renew-certs | pending | low | `renew-certs (job-0489) is pending level=1` |
| job-0206 | compact-logs | pending | normal | `compact-logs (job-0206) is pending level=2` |
| job-0816 | invoice-run | pending | normal | `invoice-run (job-0816) is pending level=2` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
