"""The grafana note view: one line per job, for the platform team's wall display."""


def render(record):
    return f"{record['id']} | {record['name']} | {record['state']}"
