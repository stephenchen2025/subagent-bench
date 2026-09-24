# Watch Face view

Module: `views/watch_face.py`. Audience: mobile users.

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
| job-0227 | rotate-keys | pending | high | `job job-0227 / rotate-keys / pending ^^` |
| job-0678 | renew-certs | failed | high | `job job-0678 / renew-certs / failed ^^` |
| job-0410 | renew-certs | failed | low | `job job-0410 / renew-certs / failed vv` |
| job-0158 | renew-certs | running | high | `job job-0158 / renew-certs / running ^^` |
| job-0784 | reindex-search | pending | normal | `job job-0784 / reindex-search / pending --` |
| job-0168 | compact-logs | done | low | `job job-0168 / compact-logs / done vv` |
| job-0985 | reindex-search | failed | low | `job job-0985 / reindex-search / failed vv` |
| job-0524 | purge-cache | running | normal | `job job-0524 / purge-cache / running --` |
| job-0052 | invoice-run | running | high | `job job-0052 / invoice-run / running ^^` |
| job-0555 | renew-certs | done | normal | `job job-0555 / renew-certs / done --` |
| job-0915 | reindex-search | running | low | `job job-0915 / reindex-search / running vv` |
| job-0311 | rebuild-feed | running | low | `job job-0311 / rebuild-feed / running vv` |
| job-0378 | send-digest | failed | low | `job job-0378 / send-digest / failed vv` |
| job-0685 | export-ledger | pending | normal | `job job-0685 / export-ledger / pending --` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
