import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['sla_board', 'html_row', 'dashboard_tile', 'jira_comment', 'grafana_note', 'sheet_row', 'email_digest', 'audit_row', 'json_feed', 'cli_table', 'pager_line', 'mobile_push', 'log_line', 'tv_wall', 'voice_prompt', 'watch_face', 'wiki_table', 'rss_item', 'sms_brief', 'discord_embed']


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
