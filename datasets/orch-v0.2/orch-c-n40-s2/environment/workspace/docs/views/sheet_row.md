# Sheet Row view

Module: `views/sheet_row.py`. Audience: customer support leads.

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
| job-0344 | export-ledger | done | high | `job-0344 | export-ledger | done level=3` |
| job-0911 | renew-certs | pending | normal | `job-0911 | renew-certs | pending level=2` |
| job-0232 | export-ledger | running | normal | `job-0232 | export-ledger | running level=2` |
| job-0019 | rotate-keys | done | high | `job-0019 | rotate-keys | done level=3` |
| job-0546 | rebuild-feed | running | low | `job-0546 | rebuild-feed | running level=1` |
| job-0259 | purge-cache | done | low | `job-0259 | purge-cache | done level=1` |
| job-0180 | renew-certs | done | low | `job-0180 | renew-certs | done level=1` |
| job-0464 | rotate-keys | done | normal | `job-0464 | rotate-keys | done level=2` |
| job-0756 | compact-logs | failed | high | `job-0756 | compact-logs | failed level=3` |
| job-0999 | invoice-run | running | low | `job-0999 | invoice-run | running level=1` |
| job-0335 | compact-logs | done | normal | `job-0335 | compact-logs | done level=2` |
| job-0713 | rotate-keys | failed | high | `job-0713 | rotate-keys | failed level=3` |
| job-0707 | compact-logs | running | high | `job-0707 | compact-logs | running level=3` |
| job-0880 | resize-images | pending | high | `job-0880 | resize-images | pending level=3` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
