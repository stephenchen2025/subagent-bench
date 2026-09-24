"""Append-only JSON-lines job store.

Every module in this package reads and writes job records through this store.
"""
import json
import os


class Store:
    def __init__(self, path):
        self.path = path
        self._clock = 0
        if os.path.exists(path):
            for record in self._records():
                self._clock = max(self._clock, record.get("created", 0))

    def _records(self):
        if not os.path.exists(self.path):
            return []
        with open(self.path) as fh:
            return [json.loads(line) for line in fh if line.strip()]

    def tick(self):
        self._clock += 1
        return self._clock

    def put(self, record):
        with open(self.path, "a") as fh:
            fh.write(json.dumps(record) + "\n")

    def all(self):
        latest = {}
        for record in self._records():
            latest[record["id"]] = record
        return list(latest.values())

    def get(self, job_id):
        for record in self.all():
            if record["id"] == job_id:
                return record
        return None

    def update(self, job_id, **fields):
        record = dict(self.get(job_id))
        record.update(fields)
        self.put(record)
        return record
