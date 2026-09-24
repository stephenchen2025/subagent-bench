"""Job submission."""


def submit(store, name):
    job_id = f"job-{len(store.all()) + 1:04d}"
    record = {"id": job_id, "name": name, "created": store.tick(), "state": "pending"}
    store.put(record)
    return job_id
