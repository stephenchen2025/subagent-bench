"""The teams card view: one line per job, for release managers."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
