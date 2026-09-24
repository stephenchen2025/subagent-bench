# Email Digest view

Module: `views/email_digest.py`. Audience: customer support leads.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0278 | reindex-search | running | normal | `level=2 job-0278: reindex-search -- running` |
| job-0282 | send-digest | done | low | `level=1 job-0282: send-digest -- done` |
| job-0528 | resize-images | running | normal | `level=2 job-0528: resize-images -- running` |
| job-0917 | nightly-backup | pending | high | `level=3 job-0917: nightly-backup -- pending` |
| job-0140 | purge-cache | pending | high | `level=3 job-0140: purge-cache -- pending` |
| job-0488 | rotate-keys | done | low | `level=1 job-0488: rotate-keys -- done` |
| job-0341 | send-digest | pending | low | `level=1 job-0341: send-digest -- pending` |
| job-0926 | purge-cache | failed | normal | `level=2 job-0926: purge-cache -- failed` |
| job-0844 | invoice-run | pending | low | `level=1 job-0844: invoice-run -- pending` |
| job-0443 | rebuild-feed | pending | high | `level=3 job-0443: rebuild-feed -- pending` |
| job-0733 | send-digest | done | low | `level=1 job-0733: send-digest -- done` |
| job-0740 | renew-certs | running | normal | `level=2 job-0740: renew-certs -- running` |
| job-0560 | rotate-keys | pending | normal | `level=2 job-0560: rotate-keys -- pending` |
| job-0708 | sync-inventory | pending | high | `level=3 job-0708: sync-inventory -- pending` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
