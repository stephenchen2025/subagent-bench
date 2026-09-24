Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 30 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `cli_table`, `jira_comment`, `discord_embed`, `sla_board`, `dashboard_tile`, `invoice_note`, `html_row`, `mobile_push`, `calendar_note`, `status_badge`, `ops_ticker`, `webhook_payload`, `sheet_row`, `kiosk_screen`, `email_digest`, `markdown_list`, `printer_slip`, `voice_prompt`, `slack_alert`, `log_line`, `grafana_note`, `rss_item`, `archive_label`, `sms_brief`, `oncall_digest`, `pager_line`, `desktop_toast`, `audit_row`, `wiki_table`, `csv_line`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
