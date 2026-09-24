Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 20 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `oncall_digest`, `sms_brief`, `sla_board`, `ops_ticker`, `log_line`, `csv_line`, `voice_prompt`, `mobile_push`, `jira_comment`, `cli_table`, `webhook_payload`, `teams_card`, `desktop_toast`, `discord_embed`, `invoice_note`, `grafana_note`, `tv_wall`, `rss_item`, `archive_label`, `weekly_report`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
