# Clean the migration exports

Every export under `/workspace/data/` has to be cleaned before the new system
can import it. Each `data/<name>/SPEC.md` says exactly how, step by step, and
the steps differ from export to export.

Write each result to `clean/<name>.csv`. The importer rejects anything that
does not match the spec exactly.
