Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 20 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `sla_board`, `html_row`, `dashboard_tile`, `jira_comment`, `grafana_note`, `sheet_row`, `email_digest`, `audit_row`, `json_feed`, `cli_table`, `pager_line`, `mobile_push`, `log_line`, `tv_wall`, `voice_prompt`, `watch_face`, `wiki_table`, `rss_item`, `sms_brief`, `discord_embed`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
