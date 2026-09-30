# One log schema for every service

We are moving every legacy service's logs onto one schema (`docs/SCHEMA.md`).
For each log format in `samples/`, write `parsers/<format>.py` exposing
`parse(text) -> list[dict]` that turns a whole log file into records in that
schema. Some formats have a note in `docs/formats/`; the rest have only their
sample.

Your parsers will be run on other logs from the same services, not on these
samples, so they must handle the format, not the file.
