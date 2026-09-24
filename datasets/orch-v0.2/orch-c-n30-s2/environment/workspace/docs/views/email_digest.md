# Email Digest view

Module: `views/email_digest.py`. Audience: customer support leads.

Current layout: `name (id) is state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `[HIGH]` |
| normal | `[NORMAL]` |
| low | `[LOW]` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0437 | rotate-keys | done | normal | `rotate-keys (job-0437) is done [NORMAL]` |
| job-0656 | reindex-search | failed | low | `reindex-search (job-0656) is failed [LOW]` |
| job-0272 | rebuild-feed | done | normal | `rebuild-feed (job-0272) is done [NORMAL]` |
| job-0133 | purge-cache | done | low | `purge-cache (job-0133) is done [LOW]` |
| job-0424 | resize-images | failed | high | `resize-images (job-0424) is failed [HIGH]` |
| job-0624 | compact-logs | running | high | `compact-logs (job-0624) is running [HIGH]` |
| job-0321 | export-ledger | running | high | `export-ledger (job-0321) is running [HIGH]` |
| job-0644 | invoice-run | failed | normal | `invoice-run (job-0644) is failed [NORMAL]` |
| job-0535 | reindex-search | running | low | `reindex-search (job-0535) is running [LOW]` |
| job-0886 | rotate-keys | running | high | `rotate-keys (job-0886) is running [HIGH]` |
| job-0987 | renew-certs | failed | normal | `renew-certs (job-0987) is failed [NORMAL]` |
| job-0229 | invoice-run | running | normal | `invoice-run (job-0229) is running [NORMAL]` |
| job-0201 | resize-images | failed | normal | `resize-images (job-0201) is failed [NORMAL]` |
| job-0546 | purge-cache | done | normal | `purge-cache (job-0546) is done [NORMAL]` |

## History

- Switched from a fixed-width layout after complaints about truncation on small screens.
- Owners asked that the format stay stable because downstream parsers depend on it.
- The layout was reviewed with the design team; keep separators exactly as they are.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.

## Owners

Questions about this view go to the team that consumes it (customer support leads).
Changes to the layout itself need their sign-off; adding the priority marker does not.
