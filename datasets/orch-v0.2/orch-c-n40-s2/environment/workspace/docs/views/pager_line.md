# Pager Line view

Module: `views/pager_line.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0307 | rotate-keys | running | high | `^^ rotate-keys (job-0307) is running` |
| job-0428 | nightly-backup | running | normal | `-- nightly-backup (job-0428) is running` |
| job-0687 | resize-images | done | low | `vv resize-images (job-0687) is done` |
| job-0576 | rotate-keys | running | high | `^^ rotate-keys (job-0576) is running` |
| job-0986 | nightly-backup | failed | normal | `-- nightly-backup (job-0986) is failed` |
| job-0416 | send-digest | failed | low | `vv send-digest (job-0416) is failed` |
| job-0417 | compact-logs | done | low | `vv compact-logs (job-0417) is done` |
| job-0172 | rotate-keys | running | high | `^^ rotate-keys (job-0172) is running` |
| job-0204 | sync-inventory | running | normal | `-- sync-inventory (job-0204) is running` |
| job-0081 | rotate-keys | failed | low | `vv rotate-keys (job-0081) is failed` |
| job-0269 | sync-inventory | pending | low | `vv sync-inventory (job-0269) is pending` |
| job-0101 | nightly-backup | done | low | `vv nightly-backup (job-0101) is done` |
| job-0997 | reindex-search | failed | normal | `-- reindex-search (job-0997) is failed` |
| job-0212 | export-ledger | running | normal | `-- export-ledger (job-0212) is running` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
