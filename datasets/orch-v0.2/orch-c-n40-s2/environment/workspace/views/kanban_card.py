"""The kanban card view: one line per job, for auditors reviewing job history."""


def render(record):
    return f"{record['name']} ({record['id']}) is {record['state']}"
