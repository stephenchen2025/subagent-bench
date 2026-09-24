"""The oncall digest view: one line per job, for customer support leads."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
