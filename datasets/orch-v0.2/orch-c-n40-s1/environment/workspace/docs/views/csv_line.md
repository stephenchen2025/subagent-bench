# Csv Line view

Module: `views/csv_line.py`. Audience: the executive summary email.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `!!!` |
| normal | `!!` |
| low | `!` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0951 | nightly-backup | failed | low | `! nightly-backup (job-0951) is failed` |
| job-0218 | compact-logs | failed | high | `!!! compact-logs (job-0218) is failed` |
| job-0801 | rotate-keys | pending | normal | `!! rotate-keys (job-0801) is pending` |
| job-0768 | compact-logs | done | high | `!!! compact-logs (job-0768) is done` |
| job-0051 | invoice-run | done | normal | `!! invoice-run (job-0051) is done` |
| job-0531 | purge-cache | done | normal | `!! purge-cache (job-0531) is done` |
| job-0376 | reindex-search | done | normal | `!! reindex-search (job-0376) is done` |
| job-0442 | sync-inventory | failed | high | `!!! sync-inventory (job-0442) is failed` |
| job-0260 | purge-cache | pending | low | `! purge-cache (job-0260) is pending` |
| job-0334 | renew-certs | pending | low | `! renew-certs (job-0334) is pending` |
| job-0111 | sync-inventory | failed | low | `! sync-inventory (job-0111) is failed` |
| job-0505 | sync-inventory | running | high | `!!! sync-inventory (job-0505) is running` |
| job-0195 | reindex-search | pending | low | `! reindex-search (job-0195) is pending` |
| job-0552 | send-digest | pending | low | `! send-digest (job-0552) is pending` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
