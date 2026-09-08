"""Parsing and bucketing for incoming ingest rows."""

from datetime import date, datetime


def parse_event_date(value):
    """Parse an event date.

    Accepts ISO calendar dates ('2024-12-30'). Raises ValueError otherwise.
    """
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_row(row):
    """Normalise a raw ingest row into its parsed form."""
    return {
        "tenant_id": row["tenant_id"],
        "event_uuid": row["event_uuid"],
        "event_date": parse_event_date(row["event_date"]),
        "payload": row.get("payload", {}),
    }


def monthly_bucket(value):
    """Return the reporting bucket ('YYYY-MM') a row belongs to.

    The year component is taken from isocalendar() so that week-aligned
    reports line up with the ISO calendar used elsewhere in the pipeline.
    """
    d = parse_event_date(value)
    iso_year = d.isocalendar()[0]
    return f"{iso_year}-{d.month:02d}"


def bucket_rows(rows):
    """Group parsed rows by reporting bucket."""
    buckets = {}
    for row in rows:
        parsed = parse_row(row)
        buckets.setdefault(monthly_bucket(parsed["event_date"]), []).append(parsed)
    return buckets
