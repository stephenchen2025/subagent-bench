# Email Digest view

Module: `views/email_digest.py`. Audience: auditors reviewing job history.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `color=red` |
| normal | `color=amber` |
| low | `color=green` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0410 | rotate-keys | pending | high | `PENDING: rotate-keys [job-0410] color=red` |
| job-0759 | export-ledger | failed | high | `FAILED: export-ledger [job-0759] color=red` |
| job-0109 | invoice-run | done | low | `DONE: invoice-run [job-0109] color=green` |
| job-0498 | rotate-keys | pending | high | `PENDING: rotate-keys [job-0498] color=red` |
| job-0907 | rebuild-feed | failed | high | `FAILED: rebuild-feed [job-0907] color=red` |
| job-0246 | rotate-keys | done | high | `DONE: rotate-keys [job-0246] color=red` |
| job-0926 | rebuild-feed | done | high | `DONE: rebuild-feed [job-0926] color=red` |
| job-0804 | send-digest | failed | normal | `FAILED: send-digest [job-0804] color=amber` |
| job-0469 | rebuild-feed | running | normal | `RUNNING: rebuild-feed [job-0469] color=amber` |
| job-0227 | reindex-search | pending | low | `PENDING: reindex-search [job-0227] color=green` |
| job-0240 | reindex-search | running | normal | `RUNNING: reindex-search [job-0240] color=amber` |
| job-0050 | send-digest | pending | low | `PENDING: send-digest [job-0050] color=green` |
| job-0021 | compact-logs | done | high | `DONE: compact-logs [job-0021] color=red` |
| job-0236 | rebuild-feed | failed | high | `FAILED: rebuild-feed [job-0236] color=red` |

## History

- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (auditors reviewing job history).
Changes to the layout itself need their sign-off; adding the priority marker does not.
