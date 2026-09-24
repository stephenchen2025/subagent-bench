"""S -- small fix. Nothing to delegate.

One bug, one file, and the failing test named in the instruction. A solo agent
fixes it in a handful of steps. A subagent adds a brief, a cold start and a
second read of the same file, and returns nothing the lead could not have done
itself. The score is the same either way; what S measures is the cost of
delegating by reflex (ORCHESTRATOR.md 5.2).
"""

from orch.task import SOLO, OrchTask, rng_for, task_id

FAMILY = "S"
SIZES = (1,)

VARIANTS = [
    {
        "module": "paging",
        "buggy": '''"""Pagination helpers."""


def paginate(items, page, per_page):
    """Return page `page` (1-indexed) of `items`, `per_page` items per page."""
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be positive")
    start = page * per_page
    return items[start:start + per_page]
''',
        "fixed": '''"""Pagination helpers."""


def paginate(items, page, per_page):
    """Return page `page` (1-indexed) of `items`, `per_page` items per page."""
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page must be positive")
    start = (page - 1) * per_page
    return items[start:start + per_page]
''',
        "test": '''    def test_first_page(self):
        self.assertEqual(paging.paginate(list(range(10)), 1, 3), [0, 1, 2])
''',
        "hidden": '''def check_pages():
    from textkit import paging
    items = list(range(10))
    assert paging.paginate(items, 1, 3) == [0, 1, 2]
    assert paging.paginate(items, 2, 3) == [3, 4, 5]
    assert paging.paginate(items, 4, 3) == [9]
    assert paging.paginate(items, 5, 3) == []


def check_errors():
    from textkit import paging
    for args in ((0, 3), (1, 0)):
        try:
            paging.paginate([1], *args)
        except ValueError:
            continue
        raise AssertionError(args)
''',
        "checks": ["check_pages", "check_errors"],
    },
    {
        "module": "chunks",
        "buggy": '''"""Chunking helpers."""


def chunk(seq, size):
    """Split `seq` into lists of `size`; the last chunk may be shorter."""
    if size < 1:
        raise ValueError("size must be positive")
    return [list(seq[i:i + size]) for i in range(0, len(seq) - size + 1, size)]
''',
        "fixed": '''"""Chunking helpers."""


def chunk(seq, size):
    """Split `seq` into lists of `size`; the last chunk may be shorter."""
    if size < 1:
        raise ValueError("size must be positive")
    return [list(seq[i:i + size]) for i in range(0, len(seq), size)]
''',
        "test": '''    def test_partial_tail(self):
        self.assertEqual(chunks.chunk([1, 2, 3, 4, 5], 2), [[1, 2], [3, 4], [5]])
''',
        "hidden": '''def check_chunks():
    from textkit import chunks
    assert chunks.chunk([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]
    assert chunks.chunk([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]
    assert chunks.chunk([], 3) == []
    assert chunks.chunk("abcde", 5) == [["a", "b", "c", "d", "e"]]


def check_errors():
    from textkit import chunks
    try:
        chunks.chunk([1], 0)
    except ValueError:
        return
    raise AssertionError("no ValueError")
''',
        "checks": ["check_chunks", "check_errors"],
    },
    {
        "module": "ranges",
        "buggy": '''"""Range helpers."""


def clamp(value, low, high):
    """Limit `value` to the closed interval [low, high]."""
    if low > high:
        raise ValueError("low must not exceed high")
    return max(high, min(low, value))
''',
        "fixed": '''"""Range helpers."""


def clamp(value, low, high):
    """Limit `value` to the closed interval [low, high]."""
    if low > high:
        raise ValueError("low must not exceed high")
    return max(low, min(high, value))
''',
        "test": '''    def test_inside(self):
        self.assertEqual(ranges.clamp(5, 0, 10), 5)
''',
        "hidden": '''def check_clamp():
    from textkit import ranges
    assert ranges.clamp(5, 0, 10) == 5
    assert ranges.clamp(-3, 0, 10) == 0
    assert ranges.clamp(99, 0, 10) == 10
    assert ranges.clamp(0, 0, 0) == 0


def check_errors():
    from textkit import ranges
    try:
        ranges.clamp(1, 5, 2)
    except ValueError:
        return
    raise AssertionError("no ValueError")
''',
        "checks": ["check_clamp", "check_errors"],
    },
]

TEST_TEMPLATE = '''import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from textkit import {module}  # noqa: E402


class Test{title}(unittest.TestCase):
{test}

if __name__ == "__main__":
    unittest.main()
'''

INSTRUCTION = """\
`python -m unittest tests/test_{module}.py` fails. Fix the bug in
`textkit/{module}.py` so it passes. Don't change the test.
"""


def generate(size, seed):
    rng = rng_for(FAMILY, size, seed)
    variant = VARIANTS[rng.randrange(len(VARIANTS))]
    module = variant["module"]
    files = {
        "textkit/__init__.py": "",
        f"textkit/{module}.py": variant["buggy"],
        f"tests/test_{module}.py": TEST_TEMPLATE.format(
            module=module, title=module.title(), test=variant["test"]
        ),
    }
    return OrchTask(
        id=task_id(FAMILY, size, seed),
        family=FAMILY,
        size=size,
        seed=seed,
        label=SOLO,
        instruction=INSTRUCTION.format(module=module),
        files=files,
        truth={"checks": variant["checks"], "module": module},
        solution=f"cat > textkit/{module}.py <<'PYEOF'\n{variant['fixed']}PYEOF\n",
        work_items=[module],
        hidden_tests={"hidden_checks.py": variant["hidden"]},
    )
