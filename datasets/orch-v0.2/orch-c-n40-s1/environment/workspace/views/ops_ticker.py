"""The ops ticker view: one line per job, for the finance team's weekly review."""


def render(record):
    return f"{record['id']}: {record['name']} -- {record['state']}"
