# Invoice Note view

Module: `views/invoice_note.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0642 | send-digest | pending | low | `P3 PENDING: send-digest [job-0642]` |
| job-0525 | purge-cache | running | high | `P1 RUNNING: purge-cache [job-0525]` |
| job-0399 | reindex-search | failed | high | `P1 FAILED: reindex-search [job-0399]` |
| job-0209 | resize-images | pending | low | `P3 PENDING: resize-images [job-0209]` |
| job-0986 | compact-logs | pending | normal | `P2 PENDING: compact-logs [job-0986]` |
| job-0430 | send-digest | running | normal | `P2 RUNNING: send-digest [job-0430]` |
| job-0009 | rotate-keys | pending | low | `P3 PENDING: rotate-keys [job-0009]` |
| job-0399 | renew-certs | pending | low | `P3 PENDING: renew-certs [job-0399]` |
| job-0830 | send-digest | running | normal | `P2 RUNNING: send-digest [job-0830]` |
| job-0254 | export-ledger | running | low | `P3 RUNNING: export-ledger [job-0254]` |
| job-0004 | rebuild-feed | running | low | `P3 RUNNING: rebuild-feed [job-0004]` |
| job-0082 | rotate-keys | running | low | `P3 RUNNING: rotate-keys [job-0082]` |
| job-0752 | invoice-run | failed | low | `P3 FAILED: invoice-run [job-0752]` |
| job-0680 | invoice-run | running | high | `P1 RUNNING: invoice-run [job-0680]` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
