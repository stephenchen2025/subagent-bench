Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 30 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `slack_alert`, `html_row`, `cli_table`, `invoice_note`, `exec_summary`, `voice_prompt`, `dashboard_tile`, `json_feed`, `rss_item`, `mobile_push`, `discord_embed`, `log_line`, `sms_brief`, `kanban_card`, `jira_comment`, `oncall_digest`, `weekly_report`, `wiki_table`, `qa_checklist`, `email_subject`, `printer_slip`, `archive_label`, `pager_line`, `tv_wall`, `ops_ticker`, `webhook_payload`, `grafana_note`, `audit_row`, `sheet_row`, `status_badge`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
