# Audit Row view

Module: `views/audit_row.py`. Audience: the executive summary email.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0661 | renew-certs | done | high | `priority:high DONE: renew-certs [job-0661]` |
| job-0262 | resize-images | pending | low | `priority:low PENDING: resize-images [job-0262]` |
| job-0652 | invoice-run | running | normal | `priority:normal RUNNING: invoice-run [job-0652]` |
| job-0442 | invoice-run | running | high | `priority:high RUNNING: invoice-run [job-0442]` |
| job-0755 | purge-cache | pending | normal | `priority:normal PENDING: purge-cache [job-0755]` |
| job-0889 | compact-logs | running | low | `priority:low RUNNING: compact-logs [job-0889]` |
| job-0722 | rebuild-feed | done | high | `priority:high DONE: rebuild-feed [job-0722]` |
| job-0657 | rebuild-feed | pending | high | `priority:high PENDING: rebuild-feed [job-0657]` |
| job-0924 | reindex-search | failed | high | `priority:high FAILED: reindex-search [job-0924]` |
| job-0911 | rebuild-feed | failed | high | `priority:high FAILED: rebuild-feed [job-0911]` |
| job-0238 | nightly-backup | pending | high | `priority:high PENDING: nightly-backup [job-0238]` |
| job-0282 | send-digest | failed | low | `priority:low FAILED: send-digest [job-0282]` |
| job-0484 | purge-cache | failed | high | `priority:high FAILED: purge-cache [job-0484]` |
| job-0194 | reindex-search | running | high | `priority:high RUNNING: reindex-search [job-0194]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
