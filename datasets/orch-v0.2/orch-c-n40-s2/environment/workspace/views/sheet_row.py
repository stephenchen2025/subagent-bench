"""The sheet row view: one line per job, for customer support leads."""


def render(record):
    return f"{record['id']} | {record['name']} | {record['state']}"
