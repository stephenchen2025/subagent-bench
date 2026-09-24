"""The discord embed view: one line per job, for mobile users."""


def render(record):
    return f"{record['id']}: {record['name']} -- {record['state']}"
