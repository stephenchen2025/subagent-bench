# Email Subject view

Module: `views/email_subject.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0060 | purge-cache | pending | high | `purge-cache (job-0060) is pending P1` |
| job-0209 | reindex-search | running | normal | `reindex-search (job-0209) is running P2` |
| job-0886 | export-ledger | pending | high | `export-ledger (job-0886) is pending P1` |
| job-0565 | invoice-run | pending | low | `invoice-run (job-0565) is pending P3` |
| job-0474 | compact-logs | failed | high | `compact-logs (job-0474) is failed P1` |
| job-0185 | purge-cache | running | high | `purge-cache (job-0185) is running P1` |
| job-0038 | invoice-run | failed | high | `invoice-run (job-0038) is failed P1` |
| job-0157 | nightly-backup | failed | high | `nightly-backup (job-0157) is failed P1` |
| job-0537 | rotate-keys | done | low | `rotate-keys (job-0537) is done P3` |
| job-0567 | compact-logs | running | high | `compact-logs (job-0567) is running P1` |
| job-0790 | renew-certs | pending | low | `renew-certs (job-0790) is pending P3` |
| job-0757 | compact-logs | running | normal | `compact-logs (job-0757) is running P2` |
| job-0815 | invoice-run | done | normal | `invoice-run (job-0815) is done P2` |
| job-0720 | invoice-run | done | low | `invoice-run (job-0720) is done P3` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
