# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0070 | sync-inventory | pending | normal | `[NORMAL] job-0070 | sync-inventory | pending` |
| job-0395 | nightly-backup | running | low | `[LOW] job-0395 | nightly-backup | running` |
| job-0049 | send-digest | done | high | `[HIGH] job-0049 | send-digest | done` |
| job-0458 | send-digest | failed | normal | `[NORMAL] job-0458 | send-digest | failed` |
| job-0230 | export-ledger | failed | high | `[HIGH] job-0230 | export-ledger | failed` |
| job-0181 | send-digest | running | low | `[LOW] job-0181 | send-digest | running` |
| job-0093 | purge-cache | failed | low | `[LOW] job-0093 | purge-cache | failed` |
| job-0943 | send-digest | done | normal | `[NORMAL] job-0943 | send-digest | done` |
| job-0280 | invoice-run | done | low | `[LOW] job-0280 | invoice-run | done` |
| job-0444 | renew-certs | running | normal | `[NORMAL] job-0444 | renew-certs | running` |
| job-0766 | export-ledger | failed | low | `[LOW] job-0766 | export-ledger | failed` |
| job-0594 | invoice-run | pending | high | `[HIGH] job-0594 | invoice-run | pending` |
| job-0141 | export-ledger | failed | low | `[LOW] job-0141 | export-ledger | failed` |
| job-0821 | sync-inventory | pending | high | `[HIGH] job-0821 | sync-inventory | pending` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
