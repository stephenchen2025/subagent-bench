# Watch Face view

Module: `views/watch_face.py`. Audience: customer support leads.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `P1` |
| normal | `P2` |
| low | `P3` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0804 | rotate-keys | failed | normal | `P2 job-0804: rotate-keys -- failed` |
| job-0868 | export-ledger | running | high | `P1 job-0868: export-ledger -- running` |
| job-0828 | compact-logs | pending | normal | `P2 job-0828: compact-logs -- pending` |
| job-0352 | send-digest | failed | low | `P3 job-0352: send-digest -- failed` |
| job-0082 | purge-cache | running | low | `P3 job-0082: purge-cache -- running` |
| job-0638 | rotate-keys | running | high | `P1 job-0638: rotate-keys -- running` |
| job-0422 | send-digest | running | normal | `P2 job-0422: send-digest -- running` |
| job-0623 | reindex-search | failed | high | `P1 job-0623: reindex-search -- failed` |
| job-0992 | export-ledger | done | high | `P1 job-0992: export-ledger -- done` |
| job-0193 | export-ledger | done | high | `P1 job-0193: export-ledger -- done` |
| job-0261 | resize-images | failed | low | `P3 job-0261: resize-images -- failed` |
| job-0243 | send-digest | pending | low | `P3 job-0243: send-digest -- pending` |
| job-0840 | nightly-backup | running | low | `P3 job-0840: nightly-backup -- running` |
| job-0494 | reindex-search | running | low | `P3 job-0494: reindex-search -- running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
