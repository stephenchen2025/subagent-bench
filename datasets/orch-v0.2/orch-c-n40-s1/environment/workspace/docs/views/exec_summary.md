# Exec Summary view

Module: `views/exec_summary.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0775 | nightly-backup | pending | high | `^^ PENDING: nightly-backup [job-0775]` |
| job-0209 | reindex-search | pending | high | `^^ PENDING: reindex-search [job-0209]` |
| job-0484 | resize-images | pending | high | `^^ PENDING: resize-images [job-0484]` |
| job-0815 | reindex-search | pending | high | `^^ PENDING: reindex-search [job-0815]` |
| job-0411 | rebuild-feed | failed | low | `vv FAILED: rebuild-feed [job-0411]` |
| job-0915 | sync-inventory | running | high | `^^ RUNNING: sync-inventory [job-0915]` |
| job-0701 | resize-images | failed | high | `^^ FAILED: resize-images [job-0701]` |
| job-0353 | resize-images | done | high | `^^ DONE: resize-images [job-0353]` |
| job-0805 | renew-certs | done | low | `vv DONE: renew-certs [job-0805]` |
| job-0643 | rotate-keys | failed | high | `^^ FAILED: rotate-keys [job-0643]` |
| job-0445 | rotate-keys | running | high | `^^ RUNNING: rotate-keys [job-0445]` |
| job-0884 | resize-images | failed | low | `vv FAILED: resize-images [job-0884]` |
| job-0698 | nightly-backup | done | high | `^^ DONE: nightly-backup [job-0698]` |
| job-0966 | rotate-keys | done | low | `vv DONE: rotate-keys [job-0966]` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
