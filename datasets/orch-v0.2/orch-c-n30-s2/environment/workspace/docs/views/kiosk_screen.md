# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: the finance team's weekly review.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0678 | sync-inventory | done | normal | `!! job-0678: sync-inventory -- done` |
| job-0836 | renew-certs | running | normal | `!! job-0836: renew-certs -- running` |
| job-0532 | purge-cache | failed | high | `!!! job-0532: purge-cache -- failed` |
| job-0046 | rotate-keys | running | normal | `!! job-0046: rotate-keys -- running` |
| job-0263 | export-ledger | done | low | `! job-0263: export-ledger -- done` |
| job-0254 | reindex-search | failed | normal | `!! job-0254: reindex-search -- failed` |
| job-0258 | renew-certs | failed | normal | `!! job-0258: renew-certs -- failed` |
| job-0683 | renew-certs | failed | low | `! job-0683: renew-certs -- failed` |
| job-0866 | send-digest | pending | normal | `!! job-0866: send-digest -- pending` |
| job-0276 | renew-certs | pending | low | `! job-0276: renew-certs -- pending` |
| job-0965 | nightly-backup | pending | low | `! job-0965: nightly-backup -- pending` |
| job-0845 | rebuild-feed | done | high | `!!! job-0845: rebuild-feed -- done` |
| job-0297 | sync-inventory | done | low | `! job-0297: sync-inventory -- done` |
| job-0725 | send-digest | done | normal | `!! job-0725: send-digest -- done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
