import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['cli_table', 'jira_comment', 'discord_embed', 'sla_board', 'dashboard_tile', 'invoice_note', 'html_row', 'mobile_push', 'calendar_note', 'status_badge', 'ops_ticker', 'webhook_payload', 'sheet_row', 'kiosk_screen', 'email_digest', 'markdown_list', 'printer_slip', 'voice_prompt', 'slack_alert', 'log_line', 'grafana_note', 'rss_item', 'archive_label', 'sms_brief', 'oncall_digest', 'pager_line', 'desktop_toast', 'audit_row', 'wiki_table', 'csv_line']


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
