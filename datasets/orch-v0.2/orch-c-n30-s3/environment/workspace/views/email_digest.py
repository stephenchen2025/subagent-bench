"""The email digest view: one line per job, for the platform team's wall display."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
