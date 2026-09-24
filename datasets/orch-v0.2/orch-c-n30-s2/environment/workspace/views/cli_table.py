"""The cli table view: one line per job, for the finance team's weekly review."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
