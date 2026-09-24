# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the on-call engineer who is paged at night.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `***` |
| normal | `**` |
| low | `*` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0397 | rebuild-feed | failed | normal | `job-0397: rebuild-feed -- failed **` |
| job-0211 | resize-images | failed | normal | `job-0211: resize-images -- failed **` |
| job-0194 | compact-logs | done | low | `job-0194: compact-logs -- done *` |
| job-0136 | compact-logs | pending | high | `job-0136: compact-logs -- pending ***` |
| job-0243 | rebuild-feed | failed | low | `job-0243: rebuild-feed -- failed *` |
| job-0448 | reindex-search | pending | high | `job-0448: reindex-search -- pending ***` |
| job-0186 | rotate-keys | failed | high | `job-0186: rotate-keys -- failed ***` |
| job-0283 | reindex-search | pending | normal | `job-0283: reindex-search -- pending **` |
| job-0241 | compact-logs | failed | normal | `job-0241: compact-logs -- failed **` |
| job-0455 | invoice-run | failed | low | `job-0455: invoice-run -- failed *` |
| job-0384 | export-ledger | failed | high | `job-0384: export-ledger -- failed ***` |
| job-0722 | invoice-run | done | high | `job-0722: invoice-run -- done ***` |
| job-0796 | purge-cache | pending | high | `job-0796: purge-cache -- pending ***` |
| job-0716 | resize-images | pending | high | `job-0716: resize-images -- pending ***` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
