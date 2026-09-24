"""The csv line view: one line per job, for customer support leads."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
