#!/usr/bin/env python3
"""LH13 -- answer 48 analytics questions as SQL, graded on data you never saw.

warehouse.db is a SQLite copy of the shop's warehouse. docs/DEFINITIONS.md
defines the business terms, and every one of them is a trap for a literal
query:

- a reporting day is a Europe/Berlin day (UTC+1, UTC+2 in summer), not a UTC day;
- revenue is in EUR at the rate of the order's UTC day, net of refunds, which
  convert at the rate of the refund's UTC day;
- only `paid` orders are revenue; `refunded` ones count toward refund rates;
- deleted customers are excluded from customer counts but their orders still
  count toward revenue;
- discontinued SKUs are not in "catalogue" rankings.

The deliverable is one SELECT per question (answers/QNN.sql). The grader runs
each against a HIDDEN warehouse with the same schema and different rows, so a
query that hardcodes numbers computed on the visible copy scores nothing.

    python3 lh13_sql_reports.py --seed 1 --out /fixture
"""

import datetime as dt
import sqlite3
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import rng_for, standard_main, write  # noqa: E402

COUNTRIES = ["DE", "FR", "NL", "PL", "SE", "IT"]
CURRENCIES = ["EUR", "PLN", "SEK", "GBP"]
CATEGORIES = ["audio", "garden", "kitchen", "toys", "books", "sports"]
STATUSES = ["paid", "paid", "paid", "paid", "refunded", "cancelled", "pending"]
N_QUESTIONS = 48
DST_START, DST_END = "2026-03-29T01:00:00", "2026-10-25T01:00:00"

DEFINITIONS = f"""# Warehouse definitions

These definitions are authoritative for every report.

- **Reporting day.** Days, weeks and months are Europe/Berlin local time.
  Timestamps in the warehouse are UTC (ISO 8601). Berlin is UTC+2 from
  {DST_START}Z (inclusive) until {DST_END}Z (exclusive), and UTC+1 otherwise.
- **Weeks** start on the Monday given in the question and last 7 days.
- **Revenue** is the value of `paid` orders: the sum of qty * unit_price over
  their items, converted to EUR at the `fx_rates` rate for the order's UTC
  date, minus any refunds on those orders, each converted at the rate for the
  refund's UTC date. `fx_rates.rate_to_eur` multiplies an amount into EUR; EUR
  itself has rate 1 and no rows.
- **Order value** (for averages) is the same EUR item total, before refunds.
- Only `paid` orders count as sales. `refunded` orders were paid and then fully
  refunded. `cancelled` and `pending` orders never count.
- **Customer counts** exclude customers with a `deleted_at`. Their past orders
  still count toward revenue and SKU rankings.
- **Catalogue rankings** exclude SKUs whose product is `discontinued = 1`.
- Round money to 2 decimals and rates to 4 decimals, as SQLite's `round()` does.
"""

SCHEMA = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, country TEXT, created_at TEXT, deleted_at TEXT);
CREATE TABLE products (sku TEXT PRIMARY KEY, category TEXT, discontinued INTEGER);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, created_at TEXT, status TEXT, currency TEXT);
CREATE TABLE order_items (order_id INTEGER, sku TEXT, qty INTEGER, unit_price REAL);
CREATE TABLE refunds (id INTEGER PRIMARY KEY, order_id INTEGER, amount REAL, created_at TEXT);
CREATE TABLE fx_rates (currency TEXT, day TEXT, rate_to_eur REAL, PRIMARY KEY (currency, day));
"""

# A Berlin-local timestamp expression, used by the oracle queries.
BERLIN = (f"(CASE WHEN {{col}} >= '{DST_START}' AND {{col}} < '{DST_END}' "
          "THEN datetime({col}, '+2 hours') ELSE datetime({col}, '+1 hours') END)")


def berlin(col):
    return BERLIN.replace("{col}", col)


FX = ("(CASE WHEN {cur} = 'EUR' THEN 1.0 ELSE (SELECT rate_to_eur FROM fx_rates f "
      "WHERE f.currency = {cur} AND f.day = substr({ts}, 1, 10)) END)")


def fx(cur, ts):
    return FX.replace("{cur}", cur).replace("{ts}", ts)


ITEM_TOTAL = "(SELECT sum(qty * unit_price) FROM order_items i WHERE i.order_id = o.id)"


def populate(db_path, data_seed):
    rng = rng_for(data_seed, "rows")
    con = sqlite3.connect(db_path)
    con.executescript(SCHEMA)
    start = dt.datetime(2026, 1, 1)
    for c in CURRENCIES:
        if c == "EUR":
            continue
        base = {"PLN": 0.23, "SEK": 0.087, "GBP": 1.17}[c]
        for d in range(0, 250):
            day = (start + dt.timedelta(days=d)).date().isoformat()
            con.execute("INSERT INTO fx_rates VALUES (?,?,?)", (c, day, round(base * rng.uniform(0.97, 1.03), 5)))
    skus = []
    for i in range(60):
        sku = f"SKU-{i:03d}"
        skus.append(sku)
        con.execute("INSERT INTO products VALUES (?,?,?)", (sku, rng.choice(CATEGORIES), int(rng.random() < 0.15)))
    for cid in range(1, 401):
        created = start + dt.timedelta(days=rng.randint(0, 120))
        deleted = (created + dt.timedelta(days=rng.randint(10, 200))).isoformat() if rng.random() < 0.12 else None
        con.execute("INSERT INTO customers VALUES (?,?,?,?,?)",
                    (cid, f"customer-{cid}", rng.choice(COUNTRIES), created.isoformat(), deleted))
    rid = 1
    for oid in range(1, 4001):
        # Bias some orders to the hour around UTC midnight, where Berlin days differ.
        when = start + dt.timedelta(days=rng.randint(0, 242), seconds=rng.choice(
            [rng.randint(0, 86399), rng.randint(79200, 86399)]))
        status = rng.choice(STATUSES)
        cur = rng.choice(CURRENCIES)
        con.execute("INSERT INTO orders VALUES (?,?,?,?,?)",
                    (oid, rng.randint(1, 400), when.strftime("%Y-%m-%dT%H:%M:%S"), status, cur))
        for _ in range(rng.randint(1, 4)):
            con.execute("INSERT INTO order_items VALUES (?,?,?,?)",
                        (oid, rng.choice(skus), rng.randint(1, 5), round(rng.uniform(3, 250), 2)))
        if status == "refunded" or (status == "paid" and rng.random() < 0.08):
            total = con.execute("SELECT sum(qty*unit_price) FROM order_items WHERE order_id=?", (oid,)).fetchone()[0]
            amount = total if status == "refunded" else round(total * rng.uniform(0.1, 0.5), 2)
            refund_at = when + dt.timedelta(days=rng.randint(1, 20))
            if refund_at < dt.datetime(2026, 8, 31):
                con.execute("INSERT INTO refunds VALUES (?,?,?,?)",
                            (rid, oid, round(amount, 2), refund_at.strftime("%Y-%m-%dT%H:%M:%S")))
                rid += 1
    con.commit()
    con.close()


# --------------------------------------------------------------- question templates

def q_revenue(cat, month):
    return (f"What was **revenue** (EUR) from `{cat}` products in {month} (reporting month)? "
            "One row, one column. Attribute an order's items to categories via their SKUs; refunds on "
            "an order reduce its revenue in proportion to that category's share of the order's items.",
            f"""SELECT round(sum(cat_total * {fx('o.currency', 'o.created_at')}
                     - coalesce((SELECT sum(r.amount * {fx('o.currency', 'r.created_at')}) FROM refunds r WHERE r.order_id = o.id), 0)
                       * cat_total / {ITEM_TOTAL}), 2)
FROM (SELECT o.*, (SELECT sum(i.qty * i.unit_price) FROM order_items i JOIN products p ON p.sku = i.sku
                   WHERE i.order_id = o.id AND p.category = '{cat}') AS cat_total FROM orders o) o
WHERE o.status = 'paid' AND cat_total IS NOT NULL AND substr({berlin('o.created_at')}, 1, 7) = '{month}'""", False)


def q_active(country):
    return (f"How many **customers** in {country} were active, meaning they placed at least one sale "
            "in the 90 reporting days before 2026-09-01 (2026-06-03 to 2026-08-31 inclusive)? One number.",
            f"""SELECT count(*) FROM customers c WHERE c.country = '{country}' AND c.deleted_at IS NULL AND EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.status = 'paid'
  AND substr({berlin('o.created_at')}, 1, 10) BETWEEN '2026-06-03' AND '2026-08-31')""", False)


def q_top_skus(week):
    end = (dt.date.fromisoformat(week) + dt.timedelta(days=7)).isoformat()
    return (f"Which 3 **catalogue** SKUs sold the most units in the reporting week starting {week}? "
            "Columns: sku, units. Order by units descending, then sku ascending.",
            f"""SELECT i.sku, sum(i.qty) AS units FROM orders o JOIN order_items i ON i.order_id = o.id
JOIN products p ON p.sku = i.sku
WHERE o.status = 'paid' AND p.discontinued = 0
AND substr({berlin('o.created_at')}, 1, 10) >= '{week}' AND substr({berlin('o.created_at')}, 1, 10) < '{end}'
GROUP BY i.sku ORDER BY units DESC, i.sku ASC LIMIT 3""", True)


def q_refund_rate(currency, quarter):
    months = {"Q1": ("2026-01", "2026-03"), "Q2": ("2026-04", "2026-06")}[quarter]
    return (f"What share of {currency} orders placed in {quarter} 2026 (reporting months) were refunded "
            "in full? Denominator: paid plus refunded orders. One number, rounded to 4 decimals.",
            f"""SELECT round(1.0 * sum(o.status = 'refunded') / count(*), 4) FROM orders o
WHERE o.currency = '{currency}' AND o.status IN ('paid', 'refunded')
AND substr({berlin('o.created_at')}, 1, 7) BETWEEN '{months[0]}' AND '{months[1]}'""", False)


def q_new_customers(month):
    return (f"How many customers made their **first sale** in {month} (reporting month)? Count every "
            "such customer, deleted or not -- this is a historical count. One number.",
            f"""SELECT count(*) FROM (SELECT o.customer_id, min({berlin('o.created_at')}) AS first
FROM orders o WHERE o.status = 'paid' GROUP BY o.customer_id) WHERE substr(first, 1, 7) = '{month}'""", False)


def q_aov(country, month):
    return (f"What was the average **order value** (EUR) of sales by customers in {country} in {month} "
            "(reporting month)? Include deleted customers' orders. One number.",
            f"""SELECT round(avg({ITEM_TOTAL} * {fx('o.currency', 'o.created_at')}), 2)
FROM orders o JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'paid' AND c.country = '{country}' AND substr({berlin('o.created_at')}, 1, 7) = '{month}'""", False)


def q_status_day(day):
    return (f"How many orders of each status were placed on {day} (reporting day)? Columns: status, "
            "orders. Include every status that occurs that day; order by status ascending.",
            f"""SELECT o.status, count(*) FROM orders o WHERE substr({berlin('o.created_at')}, 1, 10) = '{day}'
GROUP BY o.status ORDER BY o.status""", True)


def q_repeat(month):
    return (f"Among customers with at least one sale in {month} (reporting month), what share had two "
            "or more sales that month? Exclude deleted customers. One number, rounded to 4 decimals.",
            f"""SELECT round(1.0 * sum(n >= 2) / count(*), 4) FROM (
  SELECT o.customer_id, count(*) AS n FROM orders o JOIN customers c ON c.id = o.customer_id
  WHERE o.status = 'paid' AND c.deleted_at IS NULL AND substr({berlin('o.created_at')}, 1, 7) = '{month}'
  GROUP BY o.customer_id)""", False)


def plan(seed):
    rng = rng_for(seed, "questions")
    months = [f"2026-{m:02d}" for m in range(1, 9)]
    mondays = [(dt.date(2026, 1, 5) + dt.timedelta(weeks=w)).isoformat() for w in range(34)]
    days = [(dt.date(2026, 1, 2) + dt.timedelta(days=d)).isoformat() for d in range(230)]
    makers = [
        lambda: q_revenue(rng.choice(CATEGORIES), rng.choice(months)),
        lambda: q_active(rng.choice(COUNTRIES)),
        lambda: q_top_skus(rng.choice(mondays)),
        lambda: q_refund_rate(rng.choice(CURRENCIES), rng.choice(["Q1", "Q2"])),
        lambda: q_new_customers(rng.choice(months)),
        lambda: q_aov(rng.choice(COUNTRIES), rng.choice(months)),
        lambda: q_status_day(rng.choice(days)),
        lambda: q_repeat(rng.choice(months)),
    ]
    # Keep only questions whose answer is non-trivial on BOTH the visible and the
    # hidden warehouse -- otherwise `SELECT 0` would pass.
    with tempfile.TemporaryDirectory() as tmp:
        visible, hidden = Path(tmp) / "v.db", Path(tmp) / "h.db"
        populate(visible, seed)
        populate(hidden, seed * 1000 + 7)
        questions, seen, i = [], set(), 0
        while len(questions) < N_QUESTIONS:
            q = makers[i % len(makers)]()
            i += 1
            if q[0] in seen:
                continue
            seen.add(q[0])
            if all(_rows(db, q[1]) not in ([], [(None,)], [(0,)], [(0.0,)]) for db in (visible, hidden)):
                questions.append(q)
    return questions


def _rows(db, sql):
    con = sqlite3.connect(db)
    try:
        rows = con.execute(sql).fetchall()
    finally:
        con.close()
    return [tuple(round(v, 2) if isinstance(v, float) else v for v in r) for r in rows]


def _hidden_db(seed, tmp):
    path = Path(tmp) / "hidden.db"
    populate(path, seed * 1000 + 7)
    return path


def generate(seed, out=None):
    questions = plan(seed)
    truth = {"seed": seed, "questions": {}}
    files = {"docs/DEFINITIONS.md": DEFINITIONS, "docs/SCHEMA.sql": SCHEMA.strip() + "\n"}
    for n, (text, sql, ordered) in enumerate(questions, 1):
        qid = f"Q{n:02d}"
        files[f"questions/{qid}.md"] = f"# {qid}\n\n{text}\n\nAnswer with one SELECT in `answers/{qid}.sql`.\n"
        truth["questions"][qid] = {"oracle_sql": sql, "ordered": ordered, "unit_chars": len(text) + 3000}
    if out is not None:
        for rel, text in files.items():
            write(Path(out) / "workspace", rel, text)
        (Path(out) / "workspace" / "answers").mkdir(parents=True, exist_ok=True)
        populate(Path(out) / "workspace" / "warehouse.db", seed)
    return truth


def grade(seed, workspace):
    """Per question: the agent's SELECT, run on a hidden warehouse with the same
    schema and different rows, returns the oracle's rows (money to 2 decimals;
    row order matters only where the question fixes it)."""
    truth = generate(seed)
    ws = Path(workspace)
    per = {}
    with tempfile.TemporaryDirectory() as tmp:
        hidden = _hidden_db(seed, tmp)
        for qid, q in truth["questions"].items():
            path = ws / "answers" / f"{qid}.sql"
            if not path.exists():
                per[qid] = 0.0
                continue
            sql = path.read_text().strip().rstrip(";")
            if not sql.lower().lstrip("( \n").startswith(("select", "with")) or ";" in sql:
                per[qid] = 0.0
                continue
            try:
                got = _rows(hidden, sql)
            except sqlite3.Error:
                per[qid] = 0.0
                continue
            want = _rows(hidden, q["oracle_sql"])
            per[qid] = float(got == want if q["ordered"] else sorted(map(repr, got)) == sorted(map(repr, want)))
    return {"reward": round(sum(per.values()) / len(per), 4), "questions": per}


def solve(seed, workspace):
    for qid, q in generate(seed)["questions"].items():
        write(Path(workspace) / "answers", f"{qid}.sql", q["oracle_sql"] + ";\n")


def shape(seed):
    t = generate(seed)
    return {"unit_chars": [q["unit_chars"] for q in t["questions"].values()],
            "judgement_turns": 5, "orchestration_turns": 10, "shared_chars": len(DEFINITIONS) + len(SCHEMA)}


ANSWER_PATH = "/workspace"
INSTRUCTION = """\
# Quarterly report queries

Finance needs the queries behind this quarter's report. Each question in
`questions/` needs one SQL query against the warehouse (`warehouse.db`, SQLite;
schema in `docs/SCHEMA.sql`). `docs/DEFINITIONS.md` defines every business
term, and the report must follow it exactly.

Write each answer as a single SELECT in `answers/QNN.sql`. The queries will be
re-run every quarter on fresh data, so they must compute the answer, not
restate it. Try them with `sqlite3 warehouse.db < answers/Q01.sql`.
"""

META = {
    "unit": "question", "kind": "SQL queries", "domain": "analytics database", "output_tokens": 1600, "needs_pytest": False, "apt": ["sqlite3"],
    "failure_mode": "business definitions a literal query gets wrong; graded on unseen data",
    "deliverable": "one SELECT per question in `answers/QNN.sql`",
    "grading": "Per question: the query, run on a hidden warehouse with the same schema and different "
               "rows, must return the oracle's rows. Reward is the mean.",
    "per_unit": "translate the question through DEFINITIONS.md (Berlin days, FX per UTC day, refunds, "
                "statuses, deleted customers, discontinued SKUs) into one query and check it on the visible data",
    "traps": [
        "**Berlin, not UTC.** Orders near UTC midnight land on the next Berlin day, and the offset "
        "changes on 29 March.",
        "**FX per day** for orders, and per refund day for refunds.",
        "**Status semantics.** `refunded` is not revenue but is in the refund-rate denominator.",
        "**Deleted customers** drop out of customer counts but not out of revenue or rankings.",
        "**Hidden data.** A query that hardcodes a number computed on the visible copy scores zero.",
    ],
}


def main(argv=None):
    standard_main(lambda s, o: generate(s, o), grade, solve, argv, answer_is_file=False)


if __name__ == "__main__":
    main()
