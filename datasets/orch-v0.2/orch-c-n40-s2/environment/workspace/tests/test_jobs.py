import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['audit_row', 'csv_line', 'email_digest', 'mobile_push', 'wiki_table', 'qa_checklist', 'discord_embed', 'log_line', 'chat_bot', 'sla_board', 'kiosk_screen', 'invoice_note', 'email_subject', 'rss_item', 'archive_label', 'cli_table', 'webhook_payload', 'printer_slip', 'teams_card', 'sms_brief', 'status_badge', 'markdown_list', 'json_feed', 'jira_comment', 'kanban_card', 'exec_summary', 'dashboard_tile', 'pager_line', 'ops_ticker', 'html_row', 'sheet_row', 'desktop_toast', 'oncall_digest', 'grafana_note', 'calendar_note', 'tv_wall', 'weekly_report', 'slack_alert', 'voice_prompt', 'watch_face']


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
