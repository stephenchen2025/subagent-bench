# Sms Brief view

Module: `views/sms_brief.py`. Audience: customer support leads.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0628 | purge-cache | failed | high | `color=red purge-cache (job-0628) is failed` |
| job-0238 | send-digest | pending | low | `color=green send-digest (job-0238) is pending` |
| job-0228 | rotate-keys | done | normal | `color=amber rotate-keys (job-0228) is done` |
| job-0689 | rotate-keys | done | low | `color=green rotate-keys (job-0689) is done` |
| job-0083 | renew-certs | failed | low | `color=green renew-certs (job-0083) is failed` |
| job-0531 | rebuild-feed | done | high | `color=red rebuild-feed (job-0531) is done` |
| job-0743 | reindex-search | pending | normal | `color=amber reindex-search (job-0743) is pending` |
| job-0874 | rebuild-feed | failed | high | `color=red rebuild-feed (job-0874) is failed` |
| job-0962 | purge-cache | pending | normal | `color=amber purge-cache (job-0962) is pending` |
| job-0380 | purge-cache | failed | high | `color=red purge-cache (job-0380) is failed` |
| job-0576 | resize-images | done | normal | `color=amber resize-images (job-0576) is done` |
| job-0275 | rotate-keys | failed | normal | `color=amber rotate-keys (job-0275) is failed` |
| job-0219 | reindex-search | running | low | `color=green reindex-search (job-0219) is running` |
| job-0513 | send-digest | pending | normal | `color=amber send-digest (job-0513) is pending` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
