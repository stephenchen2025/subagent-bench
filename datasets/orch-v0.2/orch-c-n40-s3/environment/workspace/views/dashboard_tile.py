"""The dashboard tile view: one line per job, for auditors reviewing job history."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
