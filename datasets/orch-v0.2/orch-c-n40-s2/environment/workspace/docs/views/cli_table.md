# Cli Table view

Module: `views/cli_table.py`. Audience: the executive summary email.

Current layout: `id | name | state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

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
| job-0541 | send-digest | done | low | `job-0541 | send-digest | done level=1` |
| job-0688 | invoice-run | running | high | `job-0688 | invoice-run | running level=3` |
| job-0717 | reindex-search | failed | high | `job-0717 | reindex-search | failed level=3` |
| job-0494 | renew-certs | pending | low | `job-0494 | renew-certs | pending level=1` |
| job-0543 | invoice-run | running | high | `job-0543 | invoice-run | running level=3` |
| job-0781 | renew-certs | done | low | `job-0781 | renew-certs | done level=1` |
| job-0502 | rotate-keys | pending | normal | `job-0502 | rotate-keys | pending level=2` |
| job-0712 | send-digest | failed | high | `job-0712 | send-digest | failed level=3` |
| job-0678 | nightly-backup | pending | high | `job-0678 | nightly-backup | pending level=3` |
| job-0430 | resize-images | running | normal | `job-0430 | resize-images | running level=2` |
| job-0187 | purge-cache | running | normal | `job-0187 | purge-cache | running level=2` |
| job-0091 | rotate-keys | running | high | `job-0091 | rotate-keys | running level=3` |
| job-0555 | sync-inventory | pending | low | `job-0555 | sync-inventory | pending level=1` |
| job-0606 | rebuild-feed | done | high | `job-0606 | rebuild-feed | done level=3` |

## History

- Renamed from its old module name; the old name is gone.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (the executive summary email).
Changes to the layout itself need their sign-off; adding the priority marker does not.
