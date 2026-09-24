"""The markdown list view: one line per job, for mobile users."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
