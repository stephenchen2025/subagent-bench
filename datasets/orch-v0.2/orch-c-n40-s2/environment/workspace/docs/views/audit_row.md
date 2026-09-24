# Audit Row view

Module: `views/audit_row.py`. Audience: mobile users.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0439 | nightly-backup | done | normal | `[NORMAL] job job-0439 / nightly-backup / done` |
| job-0172 | reindex-search | running | low | `[LOW] job job-0172 / reindex-search / running` |
| job-0238 | rotate-keys | failed | high | `[HIGH] job job-0238 / rotate-keys / failed` |
| job-0254 | rebuild-feed | running | normal | `[NORMAL] job job-0254 / rebuild-feed / running` |
| job-0520 | export-ledger | done | low | `[LOW] job job-0520 / export-ledger / done` |
| job-0842 | rebuild-feed | running | normal | `[NORMAL] job job-0842 / rebuild-feed / running` |
| job-0372 | send-digest | running | normal | `[NORMAL] job job-0372 / send-digest / running` |
| job-0143 | purge-cache | done | high | `[HIGH] job job-0143 / purge-cache / done` |
| job-0704 | rebuild-feed | running | high | `[HIGH] job job-0704 / rebuild-feed / running` |
| job-0817 | invoice-run | failed | low | `[LOW] job job-0817 / invoice-run / failed` |
| job-0945 | rotate-keys | done | high | `[HIGH] job job-0945 / rotate-keys / done` |
| job-0908 | invoice-run | done | high | `[HIGH] job job-0908 / invoice-run / done` |
| job-0999 | rebuild-feed | failed | low | `[LOW] job job-0999 / rebuild-feed / failed` |
| job-0656 | renew-certs | done | low | `[LOW] job job-0656 / renew-certs / done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
