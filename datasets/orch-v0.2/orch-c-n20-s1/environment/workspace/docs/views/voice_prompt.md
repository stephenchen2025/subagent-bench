# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0156 | send-digest | pending | low | `* job-0156: send-digest -- pending` |
| job-0996 | invoice-run | failed | low | `* job-0996: invoice-run -- failed` |
| job-0595 | send-digest | failed | high | `*** job-0595: send-digest -- failed` |
| job-0055 | purge-cache | done | high | `*** job-0055: purge-cache -- done` |
| job-0204 | nightly-backup | pending | high | `*** job-0204: nightly-backup -- pending` |
| job-0185 | rotate-keys | failed | normal | `** job-0185: rotate-keys -- failed` |
| job-0700 | export-ledger | done | normal | `** job-0700: export-ledger -- done` |
| job-0950 | compact-logs | done | low | `* job-0950: compact-logs -- done` |
| job-0122 | rebuild-feed | failed | low | `* job-0122: rebuild-feed -- failed` |
| job-0097 | nightly-backup | done | normal | `** job-0097: nightly-backup -- done` |
| job-0280 | rotate-keys | failed | low | `* job-0280: rotate-keys -- failed` |
| job-0367 | rebuild-feed | running | normal | `** job-0367: rebuild-feed -- running` |
| job-0805 | export-ledger | running | normal | `** job-0805: export-ledger -- running` |
| job-0724 | export-ledger | failed | low | `* job-0724: export-ledger -- failed` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
