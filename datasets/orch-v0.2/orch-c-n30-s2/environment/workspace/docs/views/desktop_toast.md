# Desktop Toast view

Module: `views/desktop_toast.py`. Audience: mobile users.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `URGENT` |
| normal | `ROUTINE` |
| low | `DEFERRABLE` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0119 | nightly-backup | running | low | `DEFERRABLE RUNNING: nightly-backup [job-0119]` |
| job-0557 | resize-images | pending | high | `URGENT PENDING: resize-images [job-0557]` |
| job-0537 | send-digest | running | low | `DEFERRABLE RUNNING: send-digest [job-0537]` |
| job-0301 | compact-logs | running | high | `URGENT RUNNING: compact-logs [job-0301]` |
| job-0946 | rotate-keys | failed | low | `DEFERRABLE FAILED: rotate-keys [job-0946]` |
| job-0231 | send-digest | failed | high | `URGENT FAILED: send-digest [job-0231]` |
| job-0618 | nightly-backup | failed | normal | `ROUTINE FAILED: nightly-backup [job-0618]` |
| job-0730 | export-ledger | failed | low | `DEFERRABLE FAILED: export-ledger [job-0730]` |
| job-0148 | purge-cache | done | normal | `ROUTINE DONE: purge-cache [job-0148]` |
| job-0532 | invoice-run | failed | normal | `ROUTINE FAILED: invoice-run [job-0532]` |
| job-0906 | send-digest | done | normal | `ROUTINE DONE: send-digest [job-0906]` |
| job-0576 | rotate-keys | pending | normal | `ROUTINE PENDING: rotate-keys [job-0576]` |
| job-0625 | renew-certs | failed | normal | `ROUTINE FAILED: renew-certs [job-0625]` |
| job-0327 | reindex-search | failed | high | `URGENT FAILED: reindex-search [job-0327]` |

## History

- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
