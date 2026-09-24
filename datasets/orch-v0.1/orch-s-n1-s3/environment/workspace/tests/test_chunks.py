import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from textkit import chunks  # noqa: E402


class TestChunks(unittest.TestCase):
    def test_partial_tail(self):
        self.assertEqual(chunks.chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])


if __name__ == "__main__":
    unittest.main()
