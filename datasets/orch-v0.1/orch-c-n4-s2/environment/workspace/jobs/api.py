"""Read-only API views."""

FIELDS = ("id", "name", "state")


def job_view(store, job_id):
    record = store.get(job_id)
    if record is None:
        raise KeyError(job_id)
    return {field: record[field] for field in FIELDS}
