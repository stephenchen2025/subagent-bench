# Kiosk Screen view

Module: `views/kiosk_screen.py`. Audience: customer support leads.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0195 | nightly-backup | pending | low | `job job-0195 / nightly-backup / pending vv` |
| job-0054 | resize-images | done | high | `job job-0054 / resize-images / done ^^` |
| job-0213 | rebuild-feed | failed | normal | `job job-0213 / rebuild-feed / failed --` |
| job-0071 | compact-logs | done | high | `job job-0071 / compact-logs / done ^^` |
| job-0278 | rebuild-feed | failed | normal | `job job-0278 / rebuild-feed / failed --` |
| job-0629 | rotate-keys | done | normal | `job job-0629 / rotate-keys / done --` |
| job-0640 | rotate-keys | pending | normal | `job job-0640 / rotate-keys / pending --` |
| job-0645 | reindex-search | running | high | `job job-0645 / reindex-search / running ^^` |
| job-0044 | resize-images | running | low | `job job-0044 / resize-images / running vv` |
| job-0091 | rebuild-feed | failed | low | `job job-0091 / rebuild-feed / failed vv` |
| job-0937 | compact-logs | running | normal | `job job-0937 / compact-logs / running --` |
| job-0922 | rotate-keys | pending | low | `job job-0922 / rotate-keys / pending vv` |
| job-0036 | send-digest | running | normal | `job job-0036 / send-digest / running --` |
| job-0479 | renew-certs | done | low | `job job-0479 / renew-certs / done vv` |

## History

- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
