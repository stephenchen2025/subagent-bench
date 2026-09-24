# Voice Prompt view

Module: `views/voice_prompt.py`. Audience: mobile users.

Current layout: `id: name -- state`. Keep it exactly as it is; only
add the priority marker described below.

## Priority marker

Show the job's priority at the end of the line, after one space:

| priority | marker |
|---|---|
| high | `^^` |
| normal | `--` |
| low | `vv` |

Jobs submitted before priorities existed have no priority and show the `normal` marker.

## Examples

Expected output once the marker is added:

| id | name | state | priority | line |
|---|---|---|---|---|
| job-0173 | rebuild-feed | done | high | `job-0173: rebuild-feed -- done ^^` |
| job-0157 | resize-images | done | high | `job-0157: resize-images -- done ^^` |
| job-0829 | nightly-backup | running | low | `job-0829: nightly-backup -- running vv` |
| job-0735 | sync-inventory | pending | high | `job-0735: sync-inventory -- pending ^^` |
| job-0271 | send-digest | running | high | `job-0271: send-digest -- running ^^` |
| job-0773 | reindex-search | running | high | `job-0773: reindex-search -- running ^^` |
| job-0057 | compact-logs | done | high | `job-0057: compact-logs -- done ^^` |
| job-0382 | resize-images | running | low | `job-0382: resize-images -- running vv` |
| job-0325 | nightly-backup | pending | normal | `job-0325: nightly-backup -- pending --` |
| job-0699 | rebuild-feed | failed | high | `job-0699: rebuild-feed -- failed ^^` |
| job-0050 | rotate-keys | failed | low | `job-0050: rotate-keys -- failed vv` |
| job-0355 | send-digest | done | low | `job-0355: send-digest -- done vv` |
| job-0237 | invoice-run | pending | low | `job-0237: invoice-run -- pending vv` |
| job-0622 | purge-cache | done | normal | `job-0622: purge-cache -- done --` |

## History

- Added the state column; before that the view only showed the job name.
- A request to add colours in the terminal was declined to keep output plain text.
- Owners asked that the format stay stable because downstream parsers depend on it.
- Localisation was considered and deferred; everything is English for now.
- Moved from the legacy notifier into views/ as part of the views consolidation.
- Renamed from its old module name; the old name is gone.
- Switched from a fixed-width layout after complaints about truncation on small screens.
- The layout was reviewed with the design team; keep separators exactly as they are.

## Owners

Questions about this view go to the team that consumes it (mobile users).
Changes to the layout itself need their sign-off; adding the priority marker does not.
