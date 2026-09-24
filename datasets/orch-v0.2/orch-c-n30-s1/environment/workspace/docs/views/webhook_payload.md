# Webhook Payload view

Module: `views/webhook_payload.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0365 | resize-images | done | high | `DONE: resize-images [job-0365] level=3` |
| job-0047 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0047] level=1` |
| job-0296 | rotate-keys | running | normal | `RUNNING: rotate-keys [job-0296] level=2` |
| job-0082 | resize-images | running | high | `RUNNING: resize-images [job-0082] level=3` |
| job-0036 | send-digest | pending | high | `PENDING: send-digest [job-0036] level=3` |
| job-0342 | export-ledger | pending | low | `PENDING: export-ledger [job-0342] level=1` |
| job-0326 | renew-certs | running | low | `RUNNING: renew-certs [job-0326] level=1` |
| job-0810 | nightly-backup | pending | high | `PENDING: nightly-backup [job-0810] level=3` |
| job-0834 | renew-certs | failed | low | `FAILED: renew-certs [job-0834] level=1` |
| job-0372 | send-digest | running | high | `RUNNING: send-digest [job-0372] level=3` |
| job-0923 | export-ledger | pending | low | `PENDING: export-ledger [job-0923] level=1` |
| job-0700 | export-ledger | pending | low | `PENDING: export-ledger [job-0700] level=1` |
| job-0798 | export-ledger | done | high | `DONE: export-ledger [job-0798] level=3` |
| job-0108 | purge-cache | done | normal | `DONE: purge-cache [job-0108] level=2` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
