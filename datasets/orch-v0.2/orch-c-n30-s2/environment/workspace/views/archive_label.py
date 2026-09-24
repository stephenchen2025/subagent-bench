"""The archive label view: one line per job, for the on-call engineer who is paged at night."""


def render(record):
    return f"{record['state'].upper()}: {record['name']} [{record['id']}]"
