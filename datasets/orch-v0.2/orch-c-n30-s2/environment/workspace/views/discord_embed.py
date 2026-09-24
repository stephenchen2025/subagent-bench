"""The discord embed view: one line per job, for auditors reviewing job history."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
