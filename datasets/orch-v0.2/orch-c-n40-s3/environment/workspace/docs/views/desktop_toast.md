# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0053 | reindex-search | pending | normal | `job-0053 | reindex-search | pending color=amber` |
| job-0164 | nightly-backup | done | normal | `job-0164 | nightly-backup | done color=amber` |
| job-0449 | nightly-backup | running | normal | `job-0449 | nightly-backup | running color=amber` |
| job-0560 | resize-images | pending | low | `job-0560 | resize-images | pending color=green` |
| job-0772 | reindex-search | running | low | `job-0772 | reindex-search | running color=green` |
| job-0049 | rotate-keys | pending | high | `job-0049 | rotate-keys | pending color=red` |
| job-0597 | export-ledger | failed | high | `job-0597 | export-ledger | failed color=red` |
| job-0686 | rebuild-feed | running | normal | `job-0686 | rebuild-feed | running color=amber` |
| job-0443 | resize-images | running | low | `job-0443 | resize-images | running color=green` |
| job-0343 | sync-inventory | running | high | `job-0343 | sync-inventory | running color=red` |
| job-0704 | invoice-run | pending | low | `job-0704 | invoice-run | pending color=green` |
| job-0042 | sync-inventory | pending | high | `job-0042 | sync-inventory | pending color=red` |
| job-0385 | reindex-search | done | normal | `job-0385 | reindex-search | done color=amber` |
| job-0835 | purge-cache | pending | low | `job-0835 | purge-cache | pending color=green` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
