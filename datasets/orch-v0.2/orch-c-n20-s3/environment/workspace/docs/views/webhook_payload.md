# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the on-call engineer who is paged at night.

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
| job-0733 | reindex-search | done | high | `job job-0733 / reindex-search / done P1` |
| job-0385 | compact-logs | failed | high | `job job-0385 / compact-logs / failed P1` |
| job-0280 | export-ledger | running | high | `job job-0280 / export-ledger / running P1` |
| job-0074 | invoice-run | done | high | `job job-0074 / invoice-run / done P1` |
| job-0672 | rotate-keys | failed | low | `job job-0672 / rotate-keys / failed P3` |
| job-0953 | nightly-backup | done | low | `job job-0953 / nightly-backup / done P3` |
| job-0598 | renew-certs | done | high | `job job-0598 / renew-certs / done P1` |
| job-0248 | reindex-search | pending | low | `job job-0248 / reindex-search / pending P3` |
| job-0008 | rotate-keys | running | high | `job job-0008 / rotate-keys / running P1` |
| job-0453 | sync-inventory | failed | low | `job job-0453 / sync-inventory / failed P3` |
| job-0797 | invoice-run | pending | normal | `job job-0797 / invoice-run / pending P2` |
| job-0970 | send-digest | pending | high | `job job-0970 / send-digest / pending P1` |
| job-0964 | rebuild-feed | failed | high | `job job-0964 / rebuild-feed / failed P1` |
| job-0193 | send-digest | failed | high | `job job-0193 / send-digest / failed P1` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
