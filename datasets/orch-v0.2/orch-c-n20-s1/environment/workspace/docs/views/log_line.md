# Log Line view

Module: `views/log_line.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0205 | rotate-keys | pending | low | `job-0205: rotate-keys -- pending level=1` |
| job-0483 | sync-inventory | failed | normal | `job-0483: sync-inventory -- failed level=2` |
| job-0881 | send-digest | running | low | `job-0881: send-digest -- running level=1` |
| job-0756 | reindex-search | done | high | `job-0756: reindex-search -- done level=3` |
| job-0314 | invoice-run | done | low | `job-0314: invoice-run -- done level=1` |
| job-0233 | reindex-search | pending | normal | `job-0233: reindex-search -- pending level=2` |
| job-0442 | nightly-backup | failed | normal | `job-0442: nightly-backup -- failed level=2` |
| job-0198 | purge-cache | pending | high | `job-0198: purge-cache -- pending level=3` |
| job-0646 | invoice-run | pending | normal | `job-0646: invoice-run -- pending level=2` |
| job-0736 | nightly-backup | running | normal | `job-0736: nightly-backup -- running level=2` |
| job-0932 | send-digest | pending | normal | `job-0932: send-digest -- pending level=2` |
| job-0296 | compact-logs | running | low | `job-0296: compact-logs -- running level=1` |
| job-0680 | renew-certs | pending | normal | `job-0680: renew-certs -- pending level=2` |
| job-0034 | purge-cache | done | high | `job-0034: purge-cache -- done level=3` |

## History

- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
