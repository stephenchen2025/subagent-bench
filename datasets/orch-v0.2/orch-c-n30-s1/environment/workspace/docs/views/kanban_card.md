# Kanban Card view

Module: `views/kanban_card.py`. Audience: the on-call engineer who is paged at night.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0622 | send-digest | pending | low | `job job-0622 / send-digest / pending level=1` |
| job-0862 | sync-inventory | failed | normal | `job job-0862 / sync-inventory / failed level=2` |
| job-0373 | resize-images | failed | low | `job job-0373 / resize-images / failed level=1` |
| job-0454 | nightly-backup | done | low | `job job-0454 / nightly-backup / done level=1` |
| job-0040 | export-ledger | pending | normal | `job job-0040 / export-ledger / pending level=2` |
| job-0935 | invoice-run | running | high | `job job-0935 / invoice-run / running level=3` |
| job-0990 | invoice-run | running | normal | `job job-0990 / invoice-run / running level=2` |
| job-0386 | send-digest | failed | high | `job job-0386 / send-digest / failed level=3` |
| job-0214 | nightly-backup | running | high | `job job-0214 / nightly-backup / running level=3` |
| job-0789 | renew-certs | done | high | `job job-0789 / renew-certs / done level=3` |
| job-0417 | send-digest | pending | low | `job job-0417 / send-digest / pending level=1` |
| job-0380 | export-ledger | running | low | `job job-0380 / export-ledger / running level=1` |
| job-0658 | invoice-run | pending | normal | `job job-0658 / invoice-run / pending level=2` |
| job-0017 | rotate-keys | pending | low | `job job-0017 / rotate-keys / pending level=1` |

## History

- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
