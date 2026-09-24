# Jira Comment view

Module: `views/jira_comment.py`. Audience: mobile users.

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
| job-0519 | purge-cache | failed | low | `P3 job-0519 | purge-cache | failed` |
| job-0291 | invoice-run | failed | high | `P1 job-0291 | invoice-run | failed` |
| job-0574 | compact-logs | done | high | `P1 job-0574 | compact-logs | done` |
| job-0333 | reindex-search | running | low | `P3 job-0333 | reindex-search | running` |
| job-0682 | renew-certs | done | high | `P1 job-0682 | renew-certs | done` |
| job-0520 | resize-images | running | low | `P3 job-0520 | resize-images | running` |
| job-0440 | rebuild-feed | done | high | `P1 job-0440 | rebuild-feed | done` |
| job-0801 | purge-cache | pending | high | `P1 job-0801 | purge-cache | pending` |
| job-0386 | rebuild-feed | done | high | `P1 job-0386 | rebuild-feed | done` |
| job-0060 | rotate-keys | done | normal | `P2 job-0060 | rotate-keys | done` |
| job-0377 | resize-images | failed | normal | `P2 job-0377 | resize-images | failed` |
| job-0268 | rebuild-feed | pending | normal | `P2 job-0268 | rebuild-feed | pending` |
| job-0927 | reindex-search | pending | normal | `P2 job-0927 | reindex-search | pending` |
| job-0698 | send-digest | pending | low | `P3 job-0698 | send-digest | pending` |

## History

- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
