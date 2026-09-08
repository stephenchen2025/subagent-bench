"""Deduplication of incoming events.

This is the live dedup path. See src/util/hashing.py for an older helper that
is no longer wired into anything.
"""

from collections import OrderedDict

WINDOW_SIZE = 4096


def dedup_key(event):
    """The identity of an event for deduplication purposes.

    Event UUIDs are only unique *within* a tenant -- two tenants can legitimately
    emit the same uuid, and collapsing across tenants silently drops data. The
    key is therefore the pair, never the uuid alone.
    """
    return (event["tenant_id"], event["event_uuid"])


def collapse_window(events, window_size=WINDOW_SIZE):
    """Collapse duplicate events within a sliding window.

    Keeps the first occurrence of each key and drops later repeats.
    """
    seen = OrderedDict()
    out = []
    for event in events:
        key = dedup_key(event)
        if key in seen:
            continue
        seen[key] = True
        out.append(event)
        while len(seen) > window_size:
            seen.popitem(last=False)
    return out
