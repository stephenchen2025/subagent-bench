import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['cli_table', 'jira_comment', 'tv_wall', 'csv_line', 'grafana_note', 'audit_row', 'archive_label', 'email_digest', 'status_badge', 'kanban_card', 'wiki_table', 'dashboard_tile', 'rss_item', 'qa_checklist', 'ops_ticker', 'watch_face', 'discord_embed', 'webhook_payload', 'desktop_toast', 'invoice_note', 'sms_brief', 'teams_card', 'pager_line', 'exec_summary', 'email_subject', 'printer_slip', 'chat_bot', 'oncall_digest', 'weekly_report', 'sheet_row', 'calendar_note', 'voice_prompt', 'kiosk_screen', 'slack_alert', 'html_row', 'mobile_push', 'log_line', 'markdown_list', 'json_feed', 'sla_board']


class TestJobs(unittest.TestCase):
    def setUp(self):
        self.store = Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))

    def test_fifo(self):
        a = producer.submit(self.store, "a")
        b = producer.submit(self.store, "b")
        self.assertEqual(scheduler.next_job(self.store)["id"], a)
        self.assertEqual(scheduler.next_job(self.store)["id"], b)

    def test_views_show_id_and_name(self):
        job = producer.submit(self.store, "build")
        for view in VIEWS:
            line = importlib.import_module(f"views.{view}").render(self.store.get(job))
            self.assertIn(job, line)
            self.assertIn("build", line)


if __name__ == "__main__":
    unittest.main()
