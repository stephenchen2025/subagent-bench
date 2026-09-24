"""The jira comment view: one line per job, for release managers."""


def render(record):
    return f"{record['id']}: {record['name']} -- {record['state']}"
