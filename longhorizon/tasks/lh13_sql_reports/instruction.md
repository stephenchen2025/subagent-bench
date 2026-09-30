# Quarterly report queries

Finance needs the queries behind this quarter's report. Each question in
`questions/` needs one SQL query against the warehouse (`warehouse.db`, SQLite;
schema in `docs/SCHEMA.sql`). `docs/DEFINITIONS.md` defines every business
term, and the report must follow it exactly.

Write each answer as a single SELECT in `answers/QNN.sql`. The queries will be
re-run every quarter on fresh data, so they must compute the answer, not
restate it. Try them with `sqlite3 warehouse.db < answers/Q01.sql`.
