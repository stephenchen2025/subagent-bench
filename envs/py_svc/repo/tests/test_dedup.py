from src.ingest.dedup import collapse_window, dedup_key


def _ev(tenant, uuid):
    return {"tenant_id": tenant, "event_uuid": uuid, "payload": {}}


def test_collapses_repeat_within_tenant():
    events = [_ev("t1", "a"), _ev("t1", "a"), _ev("t1", "b")]
    assert len(collapse_window(events)) == 2


def test_preserves_first_occurrence_order():
    events = [_ev("t1", "b"), _ev("t1", "a"), _ev("t1", "b")]
    assert [e["event_uuid"] for e in collapse_window(events)] == ["b", "a"]


def test_window_evicts_old_keys():
    events = [_ev("t1", str(i)) for i in range(10)] + [_ev("t1", "0")]
    assert len(collapse_window(events, window_size=4)) == 11


def test_key_is_tenant_scoped():
    assert dedup_key(_ev("t1", "a")) != dedup_key(_ev("t2", "a"))


def test_same_uuid_across_tenants_is_not_collapsed():
    """Two tenants may emit the same uuid. Collapsing on uuid alone drops data."""
    events = [_ev("t1", "shared"), _ev("t2", "shared")]
    kept = collapse_window(events)
    assert len(kept) == 2, "cross-tenant events must not be collapsed"
    assert {e["tenant_id"] for e in kept} == {"t1", "t2"}
