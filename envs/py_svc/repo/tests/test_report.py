"""Reporting tests.

These have been red since the reporting rewrite landed; the rollup helpers they
import were never updated. Unrelated to ingest.
"""

import pytest

from src.ingest.parse import bucket_rows


def _rows():
    return [
        {"tenant_id": "t1", "event_uuid": "a", "event_date": "2024-06-14"},
        {"tenant_id": "t1", "event_uuid": "b", "event_date": "2024-06-15"},
    ]


def test_rollup_totals_include_tenant_column():
    buckets = bucket_rows(_rows())
    rollup = {k: {"count": len(v)} for k, v in buckets.items()}
    assert rollup["2024-06"]["tenant_id"] == "t1"


def test_rollup_emits_percentage_of_total():
    buckets = bucket_rows(_rows())
    rollup = {k: {"count": len(v)} for k, v in buckets.items()}
    assert rollup["2024-06"]["pct_of_total"] == pytest.approx(1.0)


def test_rollup_sorted_by_descending_count():
    buckets = bucket_rows(_rows())
    ordered = sorted(buckets.items(), key=lambda kv: kv[1]["count"], reverse=True)
    assert ordered[0][0] == "2024-06"
