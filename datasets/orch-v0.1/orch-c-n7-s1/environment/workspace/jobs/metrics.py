"""Counters for the dashboard."""
from collections import Counter


def counts_by_state(store):
    return dict(Counter(r["state"] for r in store.all()))
