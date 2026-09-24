"""The html row view: one line per job, for the executive summary email."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
