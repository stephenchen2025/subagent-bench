"""The wiki table view: one line per job, for release managers."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
