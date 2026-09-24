# Cli Table view

Module: `views/cli_table.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0454 | export-ledger | running | low | `level=1 job job-0454 / export-ledger / running` |
| job-0309 | rebuild-feed | pending | normal | `level=2 job job-0309 / rebuild-feed / pending` |
| job-0752 | compact-logs | pending | high | `level=3 job job-0752 / compact-logs / pending` |
| job-0164 | rotate-keys | pending | normal | `level=2 job job-0164 / rotate-keys / pending` |
| job-0496 | reindex-search | running | normal | `level=2 job job-0496 / reindex-search / running` |
| job-0420 | resize-images | running | high | `level=3 job job-0420 / resize-images / running` |
| job-0043 | rebuild-feed | failed | high | `level=3 job job-0043 / rebuild-feed / failed` |
| job-0447 | purge-cache | pending | normal | `level=2 job job-0447 / purge-cache / pending` |
| job-0651 | rebuild-feed | pending | high | `level=3 job job-0651 / rebuild-feed / pending` |
| job-0621 | rebuild-feed | failed | low | `level=1 job job-0621 / rebuild-feed / failed` |
| job-0591 | rebuild-feed | running | normal | `level=2 job job-0591 / rebuild-feed / running` |
| job-0378 | nightly-backup | done | high | `level=3 job job-0378 / nightly-backup / done` |
| job-0218 | rebuild-feed | failed | high | `level=3 job job-0218 / rebuild-feed / failed` |
| job-0284 | purge-cache | pending | low | `level=1 job job-0284 / purge-cache / pending` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
