"""The qa checklist view: one line per job, for customer support leads."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
