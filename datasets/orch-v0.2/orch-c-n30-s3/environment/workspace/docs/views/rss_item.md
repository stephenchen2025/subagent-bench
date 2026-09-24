# Rss Item view

Module: `views/rss_item.py`. Audience: customer support leads.

Current layout: `id: name -- state`. Keep it exactly as it is; only
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
| job-0873 | resize-images | failed | low | `DEFERRABLE job-0873: resize-images -- failed` |
| job-0951 | invoice-run | pending | normal | `ROUTINE job-0951: invoice-run -- pending` |
| job-0206 | nightly-backup | done | normal | `ROUTINE job-0206: nightly-backup -- done` |
| job-0760 | send-digest | done | low | `DEFERRABLE job-0760: send-digest -- done` |
| job-0592 | nightly-backup | pending | normal | `ROUTINE job-0592: nightly-backup -- pending` |
| job-0979 | sync-inventory | done | low | `DEFERRABLE job-0979: sync-inventory -- done` |
| job-0698 | compact-logs | done | high | `URGENT job-0698: compact-logs -- done` |
| job-0820 | resize-images | done | low | `DEFERRABLE job-0820: resize-images -- done` |
| job-0977 | resize-images | running | low | `DEFERRABLE job-0977: resize-images -- running` |
| job-0052 | invoice-run | failed | low | `DEFERRABLE job-0052: invoice-run -- failed` |
| job-0825 | invoice-run | failed | normal | `ROUTINE job-0825: invoice-run -- failed` |
| job-0218 | rotate-keys | running | high | `URGENT job-0218: rotate-keys -- running` |
| job-0127 | rebuild-feed | failed | high | `URGENT job-0127: rebuild-feed -- failed` |
| job-0912 | rotate-keys | running | low | `DEFERRABLE job-0912: rotate-keys -- running` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
