"""Hashing helpers.

NOTE: dedupe_rows below predates src/ingest/dedup.py and is no longer called
from anywhere in the codebase. It is kept only because an external script is
rumoured to import it; grep before deleting.
"""

import hashlib


def stable_hash(value):
    """A stable hex digest for a string value."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def dedupe_rows(rows):
    """Drop rows sharing an event_uuid.

    Deprecated: keys on the uuid alone, which collapses events across tenants.
    """
    seen = set()
    out = []
    for row in rows:
        uuid = row["event_uuid"]
        if uuid in seen:
            continue
        seen.add(uuid)
        out.append(row)
    return out
