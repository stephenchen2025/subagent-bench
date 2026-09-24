# Jira Comment view

Module: `views/jira_comment.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0537 | resize-images | failed | low | `FAILED: resize-images [job-0537] DEFERRABLE` |
| job-0555 | resize-images | pending | low | `PENDING: resize-images [job-0555] DEFERRABLE` |
| job-0740 | resize-images | pending | low | `PENDING: resize-images [job-0740] DEFERRABLE` |
| job-0870 | invoice-run | pending | normal | `PENDING: invoice-run [job-0870] ROUTINE` |
| job-0633 | sync-inventory | pending | normal | `PENDING: sync-inventory [job-0633] ROUTINE` |
| job-0626 | resize-images | failed | low | `FAILED: resize-images [job-0626] DEFERRABLE` |
| job-0906 | renew-certs | failed | low | `FAILED: renew-certs [job-0906] DEFERRABLE` |
| job-0627 | nightly-backup | failed | high | `FAILED: nightly-backup [job-0627] URGENT` |
| job-0806 | rotate-keys | running | low | `RUNNING: rotate-keys [job-0806] DEFERRABLE` |
| job-0068 | reindex-search | running | normal | `RUNNING: reindex-search [job-0068] ROUTINE` |
| job-0007 | renew-certs | running | high | `RUNNING: renew-certs [job-0007] URGENT` |
| job-0100 | renew-certs | failed | normal | `FAILED: renew-certs [job-0100] ROUTINE` |
| job-0943 | reindex-search | failed | normal | `FAILED: reindex-search [job-0943] ROUTINE` |
| job-0203 | send-digest | pending | high | `PENDING: send-digest [job-0203] URGENT` |

## History

- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Added the state column; before that the view only showed the job name.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
