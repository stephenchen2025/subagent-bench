import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['wiki_table', 'watch_face', 'voice_prompt', 'tv_wall', 'audit_row', 'chat_bot', 'slack_alert', 'printer_slip', 'rss_item', 'teams_card', 'sheet_row', 'log_line', 'status_badge', 'webhook_payload', 'email_digest', 'weekly_report', 'sms_brief', 'email_subject', 'grafana_note', 'csv_line', 'discord_embed', 'dashboard_tile', 'exec_summary', 'desktop_toast', 'qa_checklist', 'sla_board', 'kanban_card', 'calendar_note', 'jira_comment', 'kiosk_screen']


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
