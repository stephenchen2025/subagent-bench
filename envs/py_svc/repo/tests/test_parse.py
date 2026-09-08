from datetime import date

from src.ingest.parse import bucket_rows, monthly_bucket, parse_event_date


def test_parse_iso_date():
    assert parse_event_date("2024-03-05") == date(2024, 3, 5)


def test_parse_passthrough_date():
    assert parse_event_date(date(2024, 3, 5)) == date(2024, 3, 5)


def test_bucket_midmonth():
    assert monthly_bucket("2024-06-14") == "2024-06"


def test_bucket_january():
    assert monthly_bucket("2024-01-15") == "2024-01"


def test_bucket_rows_groups_by_month():
    rows = [
        {"tenant_id": "t1", "event_uuid": "a", "event_date": "2024-06-14"},
        {"tenant_id": "t1", "event_uuid": "b", "event_date": "2024-07-02"},
    ]
    assert sorted(bucket_rows(rows)) == ["2024-06", "2024-07"]
