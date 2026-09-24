# Discord Embed view

Module: `views/discord_embed.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0799 | rotate-keys | running | low | `level=1 job-0799: rotate-keys -- running` |
| job-0171 | invoice-run | pending | high | `level=3 job-0171: invoice-run -- pending` |
| job-0768 | rotate-keys | done | high | `level=3 job-0768: rotate-keys -- done` |
| job-0139 | send-digest | failed | high | `level=3 job-0139: send-digest -- failed` |
| job-0433 | invoice-run | running | low | `level=1 job-0433: invoice-run -- running` |
| job-0257 | reindex-search | running | low | `level=1 job-0257: reindex-search -- running` |
| job-0738 | nightly-backup | done | low | `level=1 job-0738: nightly-backup -- done` |
| job-0042 | compact-logs | failed | low | `level=1 job-0042: compact-logs -- failed` |
| job-0207 | invoice-run | failed | low | `level=1 job-0207: invoice-run -- failed` |
| job-0791 | reindex-search | failed | normal | `level=2 job-0791: reindex-search -- failed` |
| job-0446 | nightly-backup | failed | high | `level=3 job-0446: nightly-backup -- failed` |
| job-0750 | nightly-backup | running | low | `level=1 job-0750: nightly-backup -- running` |
| job-0514 | renew-certs | running | low | `level=1 job-0514: renew-certs -- running` |
| job-0978 | sync-inventory | pending | high | `level=3 job-0978: sync-inventory -- pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
