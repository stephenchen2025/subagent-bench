import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['oncall_digest', 'sms_brief', 'sla_board', 'ops_ticker', 'log_line', 'csv_line', 'voice_prompt', 'mobile_push', 'jira_comment', 'cli_table', 'webhook_payload', 'teams_card', 'desktop_toast', 'discord_embed', 'invoice_note', 'grafana_note', 'tv_wall', 'rss_item', 'archive_label', 'weekly_report']


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
