# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: the platform team's wall display.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0798 | renew-certs | pending | high | `level=3 renew-certs (job-0798) is pending` |
| job-0774 | purge-cache | running | high | `level=3 purge-cache (job-0774) is running` |
| job-0712 | purge-cache | failed | low | `level=1 purge-cache (job-0712) is failed` |
| job-0389 | nightly-backup | pending | normal | `level=2 nightly-backup (job-0389) is pending` |
| job-0800 | resize-images | failed | high | `level=3 resize-images (job-0800) is failed` |
| job-0755 | resize-images | done | normal | `level=2 resize-images (job-0755) is done` |
| job-0521 | rotate-keys | done | normal | `level=2 rotate-keys (job-0521) is done` |
| job-0017 | compact-logs | running | high | `level=3 compact-logs (job-0017) is running` |
| job-0011 | rotate-keys | failed | low | `level=1 rotate-keys (job-0011) is failed` |
| job-0807 | invoice-run | pending | high | `level=3 invoice-run (job-0807) is pending` |
| job-0255 | compact-logs | running | normal | `level=2 compact-logs (job-0255) is running` |
| job-0502 | sync-inventory | pending | high | `level=3 sync-inventory (job-0502) is pending` |
| job-0243 | nightly-backup | running | low | `level=1 nightly-backup (job-0243) is running` |
| job-0868 | rotate-keys | done | low | `level=1 rotate-keys (job-0868) is done` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- Added the state column; before that the view only showed the job name.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
