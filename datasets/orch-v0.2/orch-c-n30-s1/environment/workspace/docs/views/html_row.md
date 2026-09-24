# Html Row view

Module: `views/html_row.py`. Audience: the platform team's wall display.

Current layout: `STATE: name [id]`. Keep it exactly as it is; only
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
| job-0378 | reindex-search | done | low | `DONE: reindex-search [job-0378] P3` |
| job-0457 | sync-inventory | running | high | `RUNNING: sync-inventory [job-0457] P1` |
| job-0323 | reindex-search | running | low | `RUNNING: reindex-search [job-0323] P3` |
| job-0380 | rotate-keys | failed | low | `FAILED: rotate-keys [job-0380] P3` |
| job-0052 | rebuild-feed | pending | high | `PENDING: rebuild-feed [job-0052] P1` |
| job-0908 | sync-inventory | failed | low | `FAILED: sync-inventory [job-0908] P3` |
| job-0925 | resize-images | running | high | `RUNNING: resize-images [job-0925] P1` |
| job-0568 | invoice-run | done | high | `DONE: invoice-run [job-0568] P1` |
| job-0510 | nightly-backup | running | high | `RUNNING: nightly-backup [job-0510] P1` |
| job-0695 | reindex-search | running | normal | `RUNNING: reindex-search [job-0695] P2` |
| job-0174 | invoice-run | running | low | `RUNNING: invoice-run [job-0174] P3` |
| job-0497 | invoice-run | running | normal | `RUNNING: invoice-run [job-0497] P2` |
| job-0382 | renew-certs | running | normal | `RUNNING: renew-certs [job-0382] P2` |
| job-0310 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0310] P3` |

## History

- Owners asked that the format stay stable because downstream parsers depend on it.
- A request to add colours in the terminal was declined to keep output plain text.
- Renamed from its old module name; the old name is gone.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Added the state column; before that the view only showed the job name.
- Localisation was considered and deferred; everything is English for now.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (the platform team's wall display).
Changes to the layout itself need their sign-off; adding the priority marker does not.
