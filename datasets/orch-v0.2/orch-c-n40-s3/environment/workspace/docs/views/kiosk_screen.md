# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: auditors reviewing job history.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0766 | purge-cache | pending | normal | `job-0766 | purge-cache | pending priority:normal` |
| job-0582 | rotate-keys | pending | low | `job-0582 | rotate-keys | pending priority:low` |
| job-0579 | renew-certs | failed | high | `job-0579 | renew-certs | failed priority:high` |
| job-0174 | rotate-keys | done | normal | `job-0174 | rotate-keys | done priority:normal` |
| job-0877 | sync-inventory | pending | low | `job-0877 | sync-inventory | pending priority:low` |
| job-0777 | sync-inventory | failed | low | `job-0777 | sync-inventory | failed priority:low` |
| job-0256 | rebuild-feed | failed | low | `job-0256 | rebuild-feed | failed priority:low` |
| job-0296 | sync-inventory | pending | low | `job-0296 | sync-inventory | pending priority:low` |
| job-0331 | export-ledger | running | normal | `job-0331 | export-ledger | running priority:normal` |
| job-0254 | resize-images | pending | normal | `job-0254 | resize-images | pending priority:normal` |
| job-0950 | export-ledger | pending | low | `job-0950 | export-ledger | pending priority:low` |
| job-0966 | compact-logs | done | high | `job-0966 | compact-logs | done priority:high` |
| job-0736 | nightly-backup | done | normal | `job-0736 | nightly-backup | done priority:normal` |
| job-0459 | invoice-run | pending | high | `job-0459 | invoice-run | pending priority:high` |

## History

- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
