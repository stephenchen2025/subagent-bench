# Discord Embed view

Module: `views/discord_embed.py`. Audience: the finance team's weekly review.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0501 | send-digest | done | normal | `-- send-digest (job-0501) is done` |
| job-0064 | export-ledger | done | high | `^^ export-ledger (job-0064) is done` |
| job-0305 | purge-cache | pending | low | `vv purge-cache (job-0305) is pending` |
| job-0526 | sync-inventory | done | low | `vv sync-inventory (job-0526) is done` |
| job-0828 | rotate-keys | done | low | `vv rotate-keys (job-0828) is done` |
| job-0050 | reindex-search | running | low | `vv reindex-search (job-0050) is running` |
| job-0485 | purge-cache | running | low | `vv purge-cache (job-0485) is running` |
| job-0150 | rotate-keys | pending | high | `^^ rotate-keys (job-0150) is pending` |
| job-0643 | reindex-search | done | high | `^^ reindex-search (job-0643) is done` |
| job-0583 | compact-logs | running | low | `vv compact-logs (job-0583) is running` |
| job-0737 | compact-logs | pending | normal | `-- compact-logs (job-0737) is pending` |
| job-0464 | export-ledger | failed | normal | `-- export-ledger (job-0464) is failed` |
| job-0915 | compact-logs | done | low | `vv compact-logs (job-0915) is done` |
| job-0676 | sync-inventory | done | low | `vv sync-inventory (job-0676) is done` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
