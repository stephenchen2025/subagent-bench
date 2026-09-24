# Rss Item view

Module: `views/rss_item.py`. Audience: the executive summary email.

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
| job-0160 | rotate-keys | running | normal | `color=amber job-0160 | rotate-keys | running` |
| job-0635 | nightly-backup | failed | low | `color=green job-0635 | nightly-backup | failed` |
| job-0143 | reindex-search | running | high | `color=red job-0143 | reindex-search | running` |
| job-0475 | send-digest | pending | high | `color=red job-0475 | send-digest | pending` |
| job-0561 | resize-images | done | high | `color=red job-0561 | resize-images | done` |
| job-0335 | nightly-backup | done | high | `color=red job-0335 | nightly-backup | done` |
| job-0800 | resize-images | running | high | `color=red job-0800 | resize-images | running` |
| job-0668 | resize-images | running | low | `color=green job-0668 | resize-images | running` |
| job-0316 | renew-certs | running | normal | `color=amber job-0316 | renew-certs | running` |
| job-0659 | invoice-run | running | high | `color=red job-0659 | invoice-run | running` |
| job-0725 | rebuild-feed | running | high | `color=red job-0725 | rebuild-feed | running` |
| job-0230 | rebuild-feed | pending | high | `color=red job-0230 | rebuild-feed | pending` |
| job-0173 | reindex-search | failed | low | `color=green job-0173 | reindex-search | failed` |
| job-0360 | reindex-search | failed | high | `color=red job-0360 | reindex-search | failed` |

## History

- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
