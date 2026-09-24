"""The ops ticker view: one line per job, for customer support leads."""


def render(record):
    return f"{record['id']} | {record['name']} | {record['state']}"
