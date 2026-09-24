# Sms Brief view

Module: `views/sms_brief.py`. Audience: customer support leads.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

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
| job-0061 | export-ledger | running | normal | `color=amber job-0061 | export-ledger | running` |
| job-0581 | send-digest | done | normal | `color=amber job-0581 | send-digest | done` |
| job-0672 | rotate-keys | done | normal | `color=amber job-0672 | rotate-keys | done` |
| job-0916 | resize-images | done | high | `color=red job-0916 | resize-images | done` |
| job-0317 | reindex-search | done | normal | `color=amber job-0317 | reindex-search | done` |
| job-0719 | renew-certs | pending | normal | `color=amber job-0719 | renew-certs | pending` |
| job-0177 | export-ledger | done | normal | `color=amber job-0177 | export-ledger | done` |
| job-0754 | compact-logs | pending | normal | `color=amber job-0754 | compact-logs | pending` |
| job-0967 | resize-images | pending | low | `color=green job-0967 | resize-images | pending` |
| job-0841 | renew-certs | running | high | `color=red job-0841 | renew-certs | running` |
| job-0219 | rotate-keys | failed | normal | `color=amber job-0219 | rotate-keys | failed` |
| job-0481 | compact-logs | pending | high | `color=red job-0481 | compact-logs | pending` |
| job-0023 | send-digest | running | low | `color=green job-0023 | send-digest | running` |
| job-0630 | purge-cache | pending | normal | `color=amber job-0630 | purge-cache | pending` |

## History

- Localisation was considered and deferred; everything is English for now.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
