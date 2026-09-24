Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 40 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `cli_table`, `jira_comment`, `tv_wall`, `csv_line`, `grafana_note`, `audit_row`, `archive_label`, `email_digest`, `status_badge`, `kanban_card`, `wiki_table`, `dashboard_tile`, `rss_item`, `qa_checklist`, `ops_ticker`, `watch_face`, `discord_embed`, `webhook_payload`, `desktop_toast`, `invoice_note`, `sms_brief`, `teams_card`, `pager_line`, `exec_summary`, `email_subject`, `printer_slip`, `chat_bot`, `oncall_digest`, `weekly_report`, `sheet_row`, `calendar_note`, `voice_prompt`, `kiosk_screen`, `slack_alert`, `html_row`, `mobile_push`, `log_line`, `markdown_list`, `json_feed`, `sla_board`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
