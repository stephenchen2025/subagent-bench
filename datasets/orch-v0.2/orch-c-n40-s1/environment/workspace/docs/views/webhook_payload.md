# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0714 | nightly-backup | done | high | `level=3 DONE: nightly-backup [job-0714]` |
| job-0659 | export-ledger | failed | normal | `level=2 FAILED: export-ledger [job-0659]` |
| job-0235 | send-digest | running | low | `level=1 RUNNING: send-digest [job-0235]` |
| job-0278 | reindex-search | failed | high | `level=3 FAILED: reindex-search [job-0278]` |
| job-0398 | send-digest | pending | normal | `level=2 PENDING: send-digest [job-0398]` |
| job-0179 | rebuild-feed | pending | normal | `level=2 PENDING: rebuild-feed [job-0179]` |
| job-0747 | rotate-keys | failed | high | `level=3 FAILED: rotate-keys [job-0747]` |
| job-0103 | resize-images | done | high | `level=3 DONE: resize-images [job-0103]` |
| job-0943 | sync-inventory | running | low | `level=1 RUNNING: sync-inventory [job-0943]` |
| job-0516 | compact-logs | done | normal | `level=2 DONE: compact-logs [job-0516]` |
| job-0808 | rotate-keys | running | normal | `level=2 RUNNING: rotate-keys [job-0808]` |
| job-0264 | sync-inventory | failed | normal | `level=2 FAILED: sync-inventory [job-0264]` |
| job-0366 | renew-certs | running | high | `level=3 RUNNING: renew-certs [job-0366]` |
| job-0377 | compact-logs | pending | normal | `level=2 PENDING: compact-logs [job-0377]` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
