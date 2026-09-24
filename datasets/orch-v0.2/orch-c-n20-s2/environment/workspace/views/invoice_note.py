"""The invoice note view: one line per job, for mobile users."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
