"""The slack alert view: one line per job, for release managers."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
