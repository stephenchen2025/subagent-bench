"""The teams card view: one line per job, for the finance team's weekly review."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
