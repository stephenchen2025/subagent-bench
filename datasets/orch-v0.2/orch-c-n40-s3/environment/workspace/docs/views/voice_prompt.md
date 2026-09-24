# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: auditors reviewing job history.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0252 | rotate-keys | failed | low | `job-0252 | rotate-keys | failed [LOW]` |
| job-0432 | export-ledger | pending | normal | `job-0432 | export-ledger | pending [NORMAL]` |
| job-0391 | purge-cache | done | high | `job-0391 | purge-cache | done [HIGH]` |
| job-0960 | rotate-keys | pending | low | `job-0960 | rotate-keys | pending [LOW]` |
| job-0247 | rebuild-feed | running | high | `job-0247 | rebuild-feed | running [HIGH]` |
| job-0094 | send-digest | pending | normal | `job-0094 | send-digest | pending [NORMAL]` |
| job-0238 | rebuild-feed | running | normal | `job-0238 | rebuild-feed | running [NORMAL]` |
| job-0358 | reindex-search | pending | normal | `job-0358 | reindex-search | pending [NORMAL]` |
| job-0543 | reindex-search | running | low | `job-0543 | reindex-search | running [LOW]` |
| job-0629 | reindex-search | failed | low | `job-0629 | reindex-search | failed [LOW]` |
| job-0438 | export-ledger | done | low | `job-0438 | export-ledger | done [LOW]` |
| job-0253 | send-digest | running | normal | `job-0253 | send-digest | running [NORMAL]` |
| job-0346 | send-digest | done | low | `job-0346 | send-digest | done [LOW]` |
| job-0306 | reindex-search | failed | normal | `job-0306 | reindex-search | failed [NORMAL]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
