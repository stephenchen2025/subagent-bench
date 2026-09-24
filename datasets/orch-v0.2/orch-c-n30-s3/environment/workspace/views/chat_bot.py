"""The chat bot view: one line per job, for the executive summary email."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
