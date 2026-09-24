# Json Feed view

Module: `views/json_feed.py`. Audience: release managers.

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
| job-0243 | nightly-backup | done | low | `job-0243: nightly-backup -- done vv` |
| job-0644 | rotate-keys | failed | low | `job-0644: rotate-keys -- failed vv` |
| job-0317 | send-digest | running | low | `job-0317: send-digest -- running vv` |
| job-0139 | rebuild-feed | done | low | `job-0139: rebuild-feed -- done vv` |
| job-0264 | reindex-search | done | low | `job-0264: reindex-search -- done vv` |
| job-0981 | resize-images | done | normal | `job-0981: resize-images -- done --` |
| job-0312 | sync-inventory | failed | low | `job-0312: sync-inventory -- failed vv` |
| job-0683 | purge-cache | failed | low | `job-0683: purge-cache -- failed vv` |
| job-0266 | resize-images | failed | low | `job-0266: resize-images -- failed vv` |
| job-0862 | purge-cache | pending | normal | `job-0862: purge-cache -- pending --` |
| job-0330 | nightly-backup | failed | low | `job-0330: nightly-backup -- failed vv` |
| job-0946 | resize-images | running | high | `job-0946: resize-images -- running ^^` |
| job-0330 | rotate-keys | running | normal | `job-0330: rotate-keys -- running --` |
| job-0436 | resize-images | failed | normal | `job-0436: resize-images -- failed --` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
