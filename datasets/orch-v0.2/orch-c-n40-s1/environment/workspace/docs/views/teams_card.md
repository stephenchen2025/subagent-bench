# Teams Card view

Module: `views/teams_card.py`. Audience: the on-call engineer who is paged at night.

Current layout: `name (id) is state`. Keep it exactly as it is; only
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
| job-0280 | resize-images | failed | low | `P3 resize-images (job-0280) is failed` |
| job-0573 | sync-inventory | done | normal | `P2 sync-inventory (job-0573) is done` |
| job-0448 | invoice-run | running | low | `P3 invoice-run (job-0448) is running` |
| job-0026 | reindex-search | done | normal | `P2 reindex-search (job-0026) is done` |
| job-0833 | send-digest | pending | high | `P1 send-digest (job-0833) is pending` |
| job-0085 | compact-logs | done | normal | `P2 compact-logs (job-0085) is done` |
| job-0960 | invoice-run | pending | high | `P1 invoice-run (job-0960) is pending` |
| job-0344 | renew-certs | pending | high | `P1 renew-certs (job-0344) is pending` |
| job-0104 | resize-images | pending | high | `P1 resize-images (job-0104) is pending` |
| job-0699 | renew-certs | done | high | `P1 renew-certs (job-0699) is done` |
| job-0716 | sync-inventory | pending | high | `P1 sync-inventory (job-0716) is pending` |
| job-0661 | invoice-run | pending | normal | `P2 invoice-run (job-0661) is pending` |
| job-0496 | resize-images | done | high | `P1 resize-images (job-0496) is done` |
| job-0150 | send-digest | pending | low | `P3 send-digest (job-0150) is pending` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (the on-call engineer who is paged at night).
Changes to the layout itself need their sign-off; adding the priority marker does not.
