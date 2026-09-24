# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0157 | sync-inventory | done | normal | `priority:normal job-0157 | sync-inventory | done` |
| job-0042 | send-digest | failed | low | `priority:low job-0042 | send-digest | failed` |
| job-0727 | purge-cache | pending | normal | `priority:normal job-0727 | purge-cache | pending` |
| job-0146 | rotate-keys | running | high | `priority:high job-0146 | rotate-keys | running` |
| job-0182 | sync-inventory | pending | high | `priority:high job-0182 | sync-inventory | pending` |
| job-0281 | export-ledger | failed | high | `priority:high job-0281 | export-ledger | failed` |
| job-0157 | invoice-run | failed | normal | `priority:normal job-0157 | invoice-run | failed` |
| job-0134 | export-ledger | failed | normal | `priority:normal job-0134 | export-ledger | failed` |
| job-0461 | send-digest | failed | high | `priority:high job-0461 | send-digest | failed` |
| job-0738 | rotate-keys | pending | high | `priority:high job-0738 | rotate-keys | pending` |
| job-0843 | nightly-backup | pending | low | `priority:low job-0843 | nightly-backup | pending` |
| job-0728 | resize-images | done | high | `priority:high job-0728 | resize-images | done` |
| job-0973 | sync-inventory | failed | normal | `priority:normal job-0973 | sync-inventory | failed` |
| job-0987 | send-digest | failed | high | `priority:high job-0987 | send-digest | failed` |

## History

- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
