"""Ingest pipeline entrypoint."""

import logging

from src.ingest.dedup import collapse_window
from src.ingest.parse import bucket_rows, parse_row

log = logging.getLogger(__name__)


def _load(source):
    return list(source)


def _normalise(raw_rows):
    return [parse_row(row) for row in raw_rows]


def _emit(buckets, sink):
    for bucket, rows in sorted(buckets.items()):
        sink.write(bucket, rows)
    return sum(len(rows) for rows in buckets.values())


def run(source, sink):
    """Load, deduplicate, bucket and emit a batch of ingest rows."""
    raw_rows = _load(source)
    log.info("loaded %d raw rows", len(raw_rows))

    deduped = collapse_window(raw_rows)
    log.info("collapsed %d rows to %d", len(raw_rows), len(deduped))

    buckets = bucket_rows(deduped)
    written = _emit(buckets, sink)
    log.info("wrote %d rows across %d buckets", written, len(buckets))
    return written
