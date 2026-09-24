"""Picks the next job to run."""


def next_job(store):
    pending = [r for r in store.all() if r["state"] == "pending"]
    if not pending:
        return None
    job = min(pending, key=lambda r: r["created"])
    return store.update(job["id"], state="running")
