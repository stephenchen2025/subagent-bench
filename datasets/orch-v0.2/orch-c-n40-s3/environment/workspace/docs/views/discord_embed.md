# Discord Embed view

Module: `views/discord_embed.py`. Audience: the finance team's weekly review.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0117 | nightly-backup | running | high | `level=3 job-0117 | nightly-backup | running` |
| job-0711 | export-ledger | pending | high | `level=3 job-0711 | export-ledger | pending` |
| job-0123 | resize-images | done | normal | `level=2 job-0123 | resize-images | done` |
| job-0114 | send-digest | running | low | `level=1 job-0114 | send-digest | running` |
| job-0450 | resize-images | done | normal | `level=2 job-0450 | resize-images | done` |
| job-0835 | send-digest | running | high | `level=3 job-0835 | send-digest | running` |
| job-0183 | nightly-backup | running | normal | `level=2 job-0183 | nightly-backup | running` |
| job-0806 | resize-images | running | normal | `level=2 job-0806 | resize-images | running` |
| job-0040 | reindex-search | pending | low | `level=1 job-0040 | reindex-search | pending` |
| job-0361 | reindex-search | failed | normal | `level=2 job-0361 | reindex-search | failed` |
| job-0603 | compact-logs | running | low | `level=1 job-0603 | compact-logs | running` |
| job-0508 | export-ledger | failed | high | `level=3 job-0508 | export-ledger | failed` |
| job-0467 | export-ledger | running | high | `level=3 job-0467 | export-ledger | running` |
| job-0653 | rebuild-feed | pending | normal | `level=2 job-0653 | rebuild-feed | pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the finance team's weekly review).
Changes to the layout itself need their sign-off; adding the priority marker does not.
