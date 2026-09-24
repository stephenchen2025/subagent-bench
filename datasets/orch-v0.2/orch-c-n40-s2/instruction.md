Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 40 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `audit_row`, `csv_line`, `email_digest`, `mobile_push`, `wiki_table`, `qa_checklist`, `discord_embed`, `log_line`, `chat_bot`, `sla_board`, `kiosk_screen`, `invoice_note`, `email_subject`, `rss_item`, `archive_label`, `cli_table`, `webhook_payload`, `printer_slip`, `teams_card`, `sms_brief`, `status_badge`, `markdown_list`, `json_feed`, `jira_comment`, `kanban_card`, `exec_summary`, `dashboard_tile`, `pager_line`, `ops_ticker`, `html_row`, `sheet_row`, `desktop_toast`, `oncall_digest`, `grafana_note`, `calendar_note`, `tv_wall`, `weekly_report`, `slack_alert`, `voice_prompt`, `watch_face`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
