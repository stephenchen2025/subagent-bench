Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 30 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `wiki_table`, `watch_face`, `voice_prompt`, `tv_wall`, `audit_row`, `chat_bot`, `slack_alert`, `printer_slip`, `rss_item`, `teams_card`, `sheet_row`, `log_line`, `status_badge`, `webhook_payload`, `email_digest`, `weekly_report`, `sms_brief`, `email_subject`, `grafana_note`, `csv_line`, `discord_embed`, `dashboard_tile`, `exec_summary`, `desktop_toast`, `qa_checklist`, `sla_board`, `kanban_card`, `calendar_note`, `jira_comment`, `kiosk_screen`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
