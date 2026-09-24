Add job priorities to the job system, and show them in every view.

1. `jobs/producer.py`: `submit(store, name, priority="normal")` accepts `"low"`,
   `"normal"` or `"high"` and raises `ValueError` for anything else. Existing calls
   without `priority` keep working.
2. `jobs/scheduler.py`: `next_job(store)` returns the highest-priority pending job;
   ties go to the oldest.
3. Each of the 20 views below must show the job's priority exactly as its spec in
   `docs/views/<view>.md` says. Nothing else about a view's output may change.

Views: `jira_comment`, `invoice_note`, `csv_line`, `exec_summary`, `printer_slip`, `wiki_table`, `teams_card`, `archive_label`, `discord_embed`, `sms_brief`, `qa_checklist`, `cli_table`, `markdown_list`, `mobile_push`, `webhook_payload`, `tv_wall`, `desktop_toast`, `html_row`, `slack_alert`, `kiosk_screen`.

Jobs submitted before this change have no priority. Treat them as `normal`
everywhere. `python -m unittest discover tests` must keep passing.
