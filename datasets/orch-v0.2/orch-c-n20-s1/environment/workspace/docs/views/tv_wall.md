# Tv Wall view

Module: `views/tv_wall.py`. Audience: mobile users.

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
| job-0439 | reindex-search | done | normal | `DONE: reindex-search [job-0439] P2` |
| job-0735 | reindex-search | done | low | `DONE: reindex-search [job-0735] P3` |
| job-0516 | resize-images | pending | high | `PENDING: resize-images [job-0516] P1` |
| job-0526 | send-digest | pending | normal | `PENDING: send-digest [job-0526] P2` |
| job-0241 | send-digest | failed | low | `FAILED: send-digest [job-0241] P3` |
| job-0335 | rebuild-feed | pending | low | `PENDING: rebuild-feed [job-0335] P3` |
| job-0607 | export-ledger | failed | low | `FAILED: export-ledger [job-0607] P3` |
| job-0748 | send-digest | running | low | `RUNNING: send-digest [job-0748] P3` |
| job-0046 | rebuild-feed | running | low | `RUNNING: rebuild-feed [job-0046] P3` |
| job-0665 | invoice-run | pending | high | `PENDING: invoice-run [job-0665] P1` |
| job-0404 | nightly-backup | pending | low | `PENDING: nightly-backup [job-0404] P3` |
| job-0907 | export-ledger | pending | normal | `PENDING: export-ledger [job-0907] P2` |
| job-0469 | rotate-keys | failed | low | `FAILED: rotate-keys [job-0469] P3` |
| job-0327 | export-ledger | running | low | `RUNNING: export-ledger [job-0327] P3` |

## History

- Added the state column; before that the view only showed the job name.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Renamed from its old module name; the old name is gone.
- A request to add colours in the terminal was declined to keep output plain text.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- Localisation was considered and deferred; everything is English for now.
- The layout was reviewed with the design team; keep separators exactly as they are.
- Moved from the legacy notifier into views/ as part of the views consolidation.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
