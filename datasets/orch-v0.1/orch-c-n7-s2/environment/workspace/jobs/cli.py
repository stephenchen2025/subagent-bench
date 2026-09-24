"""Terminal output."""


def format_row(record):
    return f"{record['id']}  {record['state']:<8} {record['name']}"
