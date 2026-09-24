# Sms Brief view

Module: `views/sms_brief.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0641 | invoice-run | failed | low | `job-0641 | invoice-run | failed level=1` |
| job-0992 | export-ledger | done | normal | `job-0992 | export-ledger | done level=2` |
| job-0449 | purge-cache | running | high | `job-0449 | purge-cache | running level=3` |
| job-0904 | rebuild-feed | done | low | `job-0904 | rebuild-feed | done level=1` |
| job-0934 | reindex-search | done | high | `job-0934 | reindex-search | done level=3` |
| job-0662 | reindex-search | done | low | `job-0662 | reindex-search | done level=1` |
| job-0922 | resize-images | running | normal | `job-0922 | resize-images | running level=2` |
| job-0087 | rebuild-feed | failed | normal | `job-0087 | rebuild-feed | failed level=2` |
| job-0329 | purge-cache | running | low | `job-0329 | purge-cache | running level=1` |
| job-0761 | rotate-keys | pending | low | `job-0761 | rotate-keys | pending level=1` |
| job-0533 | export-ledger | pending | normal | `job-0533 | export-ledger | pending level=2` |
| job-0198 | nightly-backup | done | normal | `job-0198 | nightly-backup | done level=2` |
| job-0931 | invoice-run | running | high | `job-0931 | invoice-run | running level=3` |
| job-0312 | nightly-backup | running | high | `job-0312 | nightly-backup | running level=3` |

## History

- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
