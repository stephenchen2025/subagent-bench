import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['slack_alert', 'html_row', 'cli_table', 'invoice_note', 'exec_summary', 'voice_prompt', 'dashboard_tile', 'json_feed', 'rss_item', 'mobile_push', 'discord_embed', 'log_line', 'sms_brief', 'kanban_card', 'jira_comment', 'oncall_digest', 'weekly_report', 'wiki_table', 'qa_checklist', 'email_subject', 'printer_slip', 'archive_label', 'pager_line', 'tv_wall', 'ops_ticker', 'webhook_payload', 'grafana_note', 'audit_row', 'sheet_row', 'status_badge']


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
