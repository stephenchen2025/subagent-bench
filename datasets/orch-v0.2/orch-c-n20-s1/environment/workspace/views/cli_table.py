"""The cli table view: one line per job, for the platform team's wall display."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
