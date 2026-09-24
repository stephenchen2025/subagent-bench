# Discord Embed view

Module: `views/discord_embed.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0816 | renew-certs | done | normal | `!! job job-0816 / renew-certs / done` |
| job-0806 | invoice-run | pending | low | `! job job-0806 / invoice-run / pending` |
| job-0905 | reindex-search | pending | low | `! job job-0905 / reindex-search / pending` |
| job-0015 | purge-cache | failed | low | `! job job-0015 / purge-cache / failed` |
| job-0731 | invoice-run | done | high | `!!! job job-0731 / invoice-run / done` |
| job-0349 | sync-inventory | pending | low | `! job job-0349 / sync-inventory / pending` |
| job-0917 | send-digest | pending | high | `!!! job job-0917 / send-digest / pending` |
| job-0237 | resize-images | running | high | `!!! job job-0237 / resize-images / running` |
| job-0716 | reindex-search | done | low | `! job job-0716 / reindex-search / done` |
| job-0417 | send-digest | running | normal | `!! job job-0417 / send-digest / running` |
| job-0477 | invoice-run | failed | normal | `!! job job-0477 / invoice-run / failed` |
| job-0603 | resize-images | pending | high | `!!! job job-0603 / resize-images / pending` |
| job-0576 | invoice-run | pending | normal | `!! job job-0576 / invoice-run / pending` |
| job-0141 | rotate-keys | failed | high | `!!! job job-0141 / rotate-keys / failed` |

## History

- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
