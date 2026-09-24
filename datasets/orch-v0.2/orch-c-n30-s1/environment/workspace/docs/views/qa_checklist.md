# Qa Checklist view

Module: `views/qa_checklist.py`. Audience: customer support leads.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0752 | rebuild-feed | done | normal | `job job-0752 / rebuild-feed / done [NORMAL]` |
| job-0665 | rotate-keys | done | low | `job job-0665 / rotate-keys / done [LOW]` |
| job-0625 | purge-cache | failed | high | `job job-0625 / purge-cache / failed [HIGH]` |
| job-0538 | purge-cache | running | low | `job job-0538 / purge-cache / running [LOW]` |
| job-0567 | compact-logs | done | normal | `job job-0567 / compact-logs / done [NORMAL]` |
| job-0859 | purge-cache | done | normal | `job job-0859 / purge-cache / done [NORMAL]` |
| job-0502 | export-ledger | failed | high | `job job-0502 / export-ledger / failed [HIGH]` |
| job-0232 | compact-logs | running | normal | `job job-0232 / compact-logs / running [NORMAL]` |
| job-0363 | reindex-search | done | low | `job job-0363 / reindex-search / done [LOW]` |
| job-0387 | rotate-keys | running | high | `job job-0387 / rotate-keys / running [HIGH]` |
| job-0659 | compact-logs | done | high | `job job-0659 / compact-logs / done [HIGH]` |
| job-0759 | resize-images | failed | normal | `job job-0759 / resize-images / failed [NORMAL]` |
| job-0032 | compact-logs | running | high | `job job-0032 / compact-logs / running [HIGH]` |
| job-0766 | export-ledger | failed | low | `job job-0766 / export-ledger / failed [LOW]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
