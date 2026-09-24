import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jobs import api, producer, scheduler  # noqa: E402
from jobs.store import Store  # noqa: E402


class TestJobs(unittest.TestCase):
    def setUp(self):
        self.store = Store(os.path.join(tempfile.mkdtemp(), "jobs.jsonl"))

    def test_fifo(self):
        a = producer.submit(self.store, "a")
        b = producer.submit(self.store, "b")
        self.assertEqual(scheduler.next_job(self.store)["id"], a)
        self.assertEqual(scheduler.next_job(self.store)["id"], b)
        self.assertIsNone(scheduler.next_job(self.store))

    def test_view(self):
        a = producer.submit(self.store, "build")
        self.assertEqual(api.job_view(self.store, a)["name"], "build")


if __name__ == "__main__":
    unittest.main()
