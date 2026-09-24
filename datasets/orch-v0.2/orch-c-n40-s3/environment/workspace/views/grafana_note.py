"""The grafana note view: one line per job, for auditors reviewing job history."""


def render(record):
    return f"{record['id']} | {record['name']} | {record['state']}"
