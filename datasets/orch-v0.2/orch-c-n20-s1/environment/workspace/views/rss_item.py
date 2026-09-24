"""The rss item view: one line per job, for the on-call engineer who is paged at night."""


def render(record):
    return f"{record['id']} | {record['name']} | {record['state']}"
