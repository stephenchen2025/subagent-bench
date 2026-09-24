# Weekly Report view

Module: `views/weekly_report.py`. Audience: customer support leads.

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
| job-0198 | export-ledger | running | low | `P3 job-0198: export-ledger -- running` |
| job-0234 | purge-cache | failed | normal | `P2 job-0234: purge-cache -- failed` |
| job-0890 | send-digest | failed | low | `P3 job-0890: send-digest -- failed` |
| job-0720 | resize-images | done | high | `P1 job-0720: resize-images -- done` |
| job-0824 | reindex-search | done | high | `P1 job-0824: reindex-search -- done` |
| job-0641 | rebuild-feed | pending | low | `P3 job-0641: rebuild-feed -- pending` |
| job-0104 | send-digest | running | high | `P1 job-0104: send-digest -- running` |
| job-0515 | export-ledger | done | high | `P1 job-0515: export-ledger -- done` |
| job-0713 | invoice-run | failed | high | `P1 job-0713: invoice-run -- failed` |
| job-0844 | rotate-keys | done | normal | `P2 job-0844: rotate-keys -- done` |
| job-0739 | sync-inventory | running | low | `P3 job-0739: sync-inventory -- running` |
| job-0937 | nightly-backup | failed | high | `P1 job-0937: nightly-backup -- failed` |
| job-0576 | nightly-backup | failed | high | `P1 job-0576: nightly-backup -- failed` |
| job-0967 | renew-certs | failed | normal | `P2 job-0967: renew-certs -- failed` |

## History

- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
