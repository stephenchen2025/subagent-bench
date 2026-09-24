Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 40 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `pager_line`, `rss_item`, `chat_bot`, `status_badge`, `mobile_push`, `json_feed`, `qa_checklist`, `exec_summary`, `wiki_table`, `log_line`, `grafana_note`, `voice_prompt`, `discord_embed`, `sheet_row`, `kiosk_screen`, `csv_line`, `sla_board`, `ops_ticker`, `teams_card`, `printer_slip`, `archive_label`, `email_digest`, `oncall_digest`, `watch_face`, `dashboard_tile`, `sms_brief`, `invoice_note`, `audit_row`, `desktop_toast`, `cli_table`, `email_subject`, `tv_wall`, `markdown_list`, `jira_comment`, `slack_alert`, `kanban_card`, `webhook_payload`, `weekly_report`, `html_row`, `calendar_note`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
