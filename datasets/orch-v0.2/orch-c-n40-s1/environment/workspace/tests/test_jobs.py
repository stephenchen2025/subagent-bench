import importlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402

VIEWS = ['pager_line', 'rss_item', 'chat_bot', 'status_badge', 'mobile_push', 'json_feed', 'qa_checklist', 'exec_summary', 'wiki_table', 'log_line', 'grafana_note', 'voice_prompt', 'discord_embed', 'sheet_row', 'kiosk_screen', 'csv_line', 'sla_board', 'ops_ticker', 'teams_card', 'printer_slip', 'archive_label', 'email_digest', 'oncall_digest', 'watch_face', 'dashboard_tile', 'sms_brief', 'invoice_note', 'audit_row', 'desktop_toast', 'cli_table', 'email_subject', 'tv_wall', 'markdown_list', 'jira_comment', 'slack_alert', 'kanban_card', 'webhook_payload', 'weekly_report', 'html_row', 'calendar_note']


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
