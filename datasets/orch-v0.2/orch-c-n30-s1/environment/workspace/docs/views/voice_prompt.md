# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: the platform team's wall display.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0985 | rotate-keys | pending | low | `priority:low job job-0985 / rotate-keys / pending` |
| job-0418 | rebuild-feed | running | high | `priority:high job job-0418 / rebuild-feed / running` |
| job-0647 | send-digest | done | high | `priority:high job job-0647 / send-digest / done` |
| job-0271 | renew-certs | failed | normal | `priority:normal job job-0271 / renew-certs / failed` |
| job-0384 | invoice-run | failed | low | `priority:low job job-0384 / invoice-run / failed` |
| job-0254 | rotate-keys | done | high | `priority:high job job-0254 / rotate-keys / done` |
| job-0017 | rotate-keys | pending | high | `priority:high job job-0017 / rotate-keys / pending` |
| job-0966 | send-digest | pending | high | `priority:high job job-0966 / send-digest / pending` |
| job-0224 | rotate-keys | running | normal | `priority:normal job job-0224 / rotate-keys / running` |
| job-0690 | nightly-backup | done | high | `priority:high job job-0690 / nightly-backup / done` |
| job-0984 | rebuild-feed | done | normal | `priority:normal job job-0984 / rebuild-feed / done` |
| job-0428 | invoice-run | failed | high | `priority:high job job-0428 / invoice-run / failed` |
| job-0978 | resize-images | failed | low | `priority:low job job-0978 / resize-images / failed` |
| job-0666 | export-ledger | running | high | `priority:high job job-0666 / export-ledger / running` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
