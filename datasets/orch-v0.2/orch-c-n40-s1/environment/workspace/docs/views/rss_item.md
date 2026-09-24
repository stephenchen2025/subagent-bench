# Rss Item view

Module: `views/rss_item.py`. Audience: mobile users.

Current layout: `id | name | state`. Keep it exactly as it is; only
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
| job-0525 | compact-logs | pending | high | `P1 job-0525 | compact-logs | pending` |
| job-0724 | resize-images | running | low | `P3 job-0724 | resize-images | running` |
| job-0736 | send-digest | done | low | `P3 job-0736 | send-digest | done` |
| job-0420 | invoice-run | pending | normal | `P2 job-0420 | invoice-run | pending` |
| job-0096 | invoice-run | done | normal | `P2 job-0096 | invoice-run | done` |
| job-0562 | compact-logs | failed | low | `P3 job-0562 | compact-logs | failed` |
| job-0517 | sync-inventory | pending | high | `P1 job-0517 | sync-inventory | pending` |
| job-0407 | rebuild-feed | pending | normal | `P2 job-0407 | rebuild-feed | pending` |
| job-0685 | nightly-backup | failed | high | `P1 job-0685 | nightly-backup | failed` |
| job-0340 | export-ledger | failed | normal | `P2 job-0340 | export-ledger | failed` |
| job-0892 | sync-inventory | done | low | `P3 job-0892 | sync-inventory | done` |
| job-0999 | nightly-backup | pending | low | `P3 job-0999 | nightly-backup | pending` |
| job-0648 | rotate-keys | running | high | `P1 job-0648 | rotate-keys | running` |
| job-0487 | compact-logs | failed | normal | `P2 job-0487 | compact-logs | failed` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
