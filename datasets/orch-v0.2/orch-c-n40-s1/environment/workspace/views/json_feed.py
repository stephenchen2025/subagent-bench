"""The json feed view: one line per job, for the executive summary email."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
