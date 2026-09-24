"""The slack alert view: one line per job, for mobile users."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
