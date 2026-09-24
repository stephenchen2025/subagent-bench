"""The mobile push view: one line per job, for the finance team's weekly review."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
