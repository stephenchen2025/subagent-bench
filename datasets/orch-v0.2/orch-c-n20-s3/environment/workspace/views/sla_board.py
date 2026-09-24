"""The sla board view: one line per job, for mobile users."""


def render(record):
    return f"{record['id']}: {record['name']} -- {record['state']}"
