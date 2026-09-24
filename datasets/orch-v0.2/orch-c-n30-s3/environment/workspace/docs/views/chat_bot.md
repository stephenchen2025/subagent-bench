# Chat Bot view

Module: `views/chat_bot.py`. Audience: the executive summary email.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the start of the line, followed by one space:

| priority | marker |
|---|---|
| high | `priority:high` |
| normal | `priority:normal` |
| low | `priority:low` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0100 | purge-cache | done | normal | `priority:normal job job-0100 / purge-cache / done` |
| job-0215 | sync-inventory | running | normal | `priority:normal job job-0215 / sync-inventory / running` |
| job-0699 | renew-certs | pending | high | `priority:high job job-0699 / renew-certs / pending` |
| job-0378 | sync-inventory | pending | normal | `priority:normal job job-0378 / sync-inventory / pending` |
| job-0937 | send-digest | done | high | `priority:high job job-0937 / send-digest / done` |
| job-0430 | send-digest | pending | low | `priority:low job job-0430 / send-digest / pending` |
| job-0656 | compact-logs | running | normal | `priority:normal job job-0656 / compact-logs / running` |
| job-0798 | reindex-search | pending | low | `priority:low job job-0798 / reindex-search / pending` |
| job-0978 | nightly-backup | done | normal | `priority:normal job job-0978 / nightly-backup / done` |
| job-0985 | rotate-keys | running | low | `priority:low job job-0985 / rotate-keys / running` |
| job-0060 | send-digest | done | low | `priority:low job job-0060 / send-digest / done` |
| job-0244 | rotate-keys | failed | normal | `priority:normal job job-0244 / rotate-keys / failed` |
| job-0870 | send-digest | failed | low | `priority:low job job-0870 / send-digest / failed` |
| job-0376 | renew-certs | done | normal | `priority:normal job job-0376 / renew-certs / done` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
