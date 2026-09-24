# Jira Comment view

Module: `views/jira_comment.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0856 | renew-certs | failed | low | `job job-0856 / renew-certs / failed P3` |
| job-0800 | rotate-keys | running | normal | `job job-0800 / rotate-keys / running P2` |
| job-0099 | reindex-search | running | high | `job job-0099 / reindex-search / running P1` |
| job-0397 | resize-images | failed | low | `job job-0397 / resize-images / failed P3` |
| job-0389 | invoice-run | done | high | `job job-0389 / invoice-run / done P1` |
| job-0644 | nightly-backup | done | normal | `job job-0644 / nightly-backup / done P2` |
| job-0776 | renew-certs | failed | normal | `job job-0776 / renew-certs / failed P2` |
| job-0897 | purge-cache | pending | low | `job job-0897 / purge-cache / pending P3` |
| job-0891 | reindex-search | failed | high | `job job-0891 / reindex-search / failed P1` |
| job-0298 | send-digest | running | normal | `job job-0298 / send-digest / running P2` |
| job-0208 | export-ledger | failed | low | `job job-0208 / export-ledger / failed P3` |
| job-0591 | renew-certs | failed | normal | `job job-0591 / renew-certs / failed P2` |
| job-0322 | nightly-backup | done | normal | `job job-0322 / nightly-backup / done P2` |
| job-0811 | rebuild-feed | failed | high | `job job-0811 / rebuild-feed / failed P1` |

## History

- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
