# Email Digest view

Module: `views/email_digest.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0361 | nightly-backup | done | high | `job-0361: nightly-backup -- done ^^` |
| job-0080 | invoice-run | pending | normal | `job-0080: invoice-run -- pending --` |
| job-0345 | send-digest | running | high | `job-0345: send-digest -- running ^^` |
| job-0109 | renew-certs | pending | high | `job-0109: renew-certs -- pending ^^` |
| job-0620 | resize-images | failed | low | `job-0620: resize-images -- failed vv` |
| job-0306 | purge-cache | pending | high | `job-0306: purge-cache -- pending ^^` |
| job-0720 | invoice-run | failed | low | `job-0720: invoice-run -- failed vv` |
| job-0862 | nightly-backup | pending | low | `job-0862: nightly-backup -- pending vv` |
| job-0055 | resize-images | pending | high | `job-0055: resize-images -- pending ^^` |
| job-0232 | invoice-run | done | normal | `job-0232: invoice-run -- done --` |
| job-0334 | resize-images | done | normal | `job-0334: resize-images -- done --` |
| job-0869 | nightly-backup | failed | normal | `job-0869: nightly-backup -- failed --` |
| job-0032 | reindex-search | running | normal | `job-0032: reindex-search -- running --` |
| job-0533 | purge-cache | done | high | `job-0533: purge-cache -- done ^^` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
