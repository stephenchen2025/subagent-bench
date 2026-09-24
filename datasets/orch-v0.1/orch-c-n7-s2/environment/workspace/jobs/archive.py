"""Compact one-line archive format."""


def pack(record):
    return "|".join([record["id"], record["name"], record["state"], str(record["created"])])


def unpack(line):
    job_id, name, state, created = line.split("|")
    return {"id": job_id, "name": name, "state": state, "created": int(created)}
