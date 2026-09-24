# Discord Embed view

Module: `views/discord_embed.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0281 | rebuild-feed | failed | normal | `job-0281 | rebuild-feed | failed P2` |
| job-0614 | sync-inventory | pending | high | `job-0614 | sync-inventory | pending P1` |
| job-0862 | renew-certs | pending | high | `job-0862 | renew-certs | pending P1` |
| job-0281 | rotate-keys | done | low | `job-0281 | rotate-keys | done P3` |
| job-0945 | purge-cache | failed | high | `job-0945 | purge-cache | failed P1` |
| job-0102 | renew-certs | done | low | `job-0102 | renew-certs | done P3` |
| job-0922 | invoice-run | done | low | `job-0922 | invoice-run | done P3` |
| job-0308 | sync-inventory | pending | normal | `job-0308 | sync-inventory | pending P2` |
| job-0978 | sync-inventory | done | normal | `job-0978 | sync-inventory | done P2` |
| job-0170 | sync-inventory | pending | high | `job-0170 | sync-inventory | pending P1` |
| job-0454 | resize-images | done | low | `job-0454 | resize-images | done P3` |
| job-0932 | send-digest | done | normal | `job-0932 | send-digest | done P2` |
| job-0445 | invoice-run | done | normal | `job-0445 | invoice-run | done P2` |
| job-0179 | rotate-keys | failed | normal | `job-0179 | rotate-keys | failed P2` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
