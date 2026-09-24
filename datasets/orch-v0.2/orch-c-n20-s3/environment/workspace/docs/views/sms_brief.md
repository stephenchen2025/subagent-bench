# Sms Brief view

Module: `views/sms_brief.py`. Audience: customer support leads.

Current layout: `job id / name / state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0980 | send-digest | running | high | `job job-0980 / send-digest / running P1` |
| job-0797 | reindex-search | running | low | `job job-0797 / reindex-search / running P3` |
| job-0758 | rebuild-feed | pending | high | `job job-0758 / rebuild-feed / pending P1` |
| job-0852 | reindex-search | running | normal | `job job-0852 / reindex-search / running P2` |
| job-0329 | send-digest | failed | low | `job job-0329 / send-digest / failed P3` |
| job-0400 | invoice-run | done | normal | `job job-0400 / invoice-run / done P2` |
| job-0102 | send-digest | done | normal | `job job-0102 / send-digest / done P2` |
| job-0279 | sync-inventory | running | normal | `job job-0279 / sync-inventory / running P2` |
| job-0698 | renew-certs | done | normal | `job job-0698 / renew-certs / done P2` |
| job-0216 | invoice-run | failed | normal | `job job-0216 / invoice-run / failed P2` |
| job-0943 | rotate-keys | done | normal | `job job-0943 / rotate-keys / done P2` |
| job-0537 | invoice-run | done | normal | `job job-0537 / invoice-run / done P2` |
| job-0483 | sync-inventory | failed | normal | `job job-0483 / sync-inventory / failed P2` |
| job-0418 | purge-cache | running | high | `job job-0418 / purge-cache / running P1` |

## History

- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Added the state column; before that the view only showed the job name.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
