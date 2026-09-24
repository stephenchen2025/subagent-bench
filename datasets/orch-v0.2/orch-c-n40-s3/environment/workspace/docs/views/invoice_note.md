# Invoice Note view

Module: `views/invoice_note.py`. Audience: release managers.

Current layout: `job id / name / state`. Keep it exactly as it is; only
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
| job-0696 | sync-inventory | running | normal | `level=2 job job-0696 / sync-inventory / running` |
| job-0808 | invoice-run | pending | normal | `level=2 job job-0808 / invoice-run / pending` |
| job-0773 | rebuild-feed | pending | high | `level=3 job job-0773 / rebuild-feed / pending` |
| job-0946 | resize-images | done | high | `level=3 job job-0946 / resize-images / done` |
| job-0710 | purge-cache | failed | low | `level=1 job job-0710 / purge-cache / failed` |
| job-0692 | rotate-keys | done | high | `level=3 job job-0692 / rotate-keys / done` |
| job-0534 | nightly-backup | pending | low | `level=1 job job-0534 / nightly-backup / pending` |
| job-0104 | reindex-search | running | low | `level=1 job job-0104 / reindex-search / running` |
| job-0134 | rebuild-feed | pending | low | `level=1 job job-0134 / rebuild-feed / pending` |
| job-0752 | rebuild-feed | failed | normal | `level=2 job job-0752 / rebuild-feed / failed` |
| job-0814 | rotate-keys | pending | normal | `level=2 job job-0814 / rotate-keys / pending` |
| job-0931 | purge-cache | running | high | `level=3 job job-0931 / purge-cache / running` |
| job-0255 | purge-cache | running | low | `level=1 job job-0255 / purge-cache / running` |
| job-0856 | export-ledger | pending | normal | `level=2 job job-0856 / export-ledger / pending` |

## History

- Localisation was considered and deferred; everything is English for now.
- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Switched from a fixed-width layout after complaints about truncation on small screens.

## Owners

Questions about this view go to the team that consumes it (release managers).
Changes to the layout itself need their sign-off; adding the priority marker does not.
