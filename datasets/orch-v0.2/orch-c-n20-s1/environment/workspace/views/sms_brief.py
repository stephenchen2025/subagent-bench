"""The sms brief view: one line per job, for the platform team's wall display."""


def render(record):
    return f"job {record['id']} / {record['name']} / {record['state']}"
