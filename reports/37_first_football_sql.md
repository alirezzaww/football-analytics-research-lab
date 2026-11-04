# Lesson 54: query football records with SQL

## Completed worked assignment

Build a small SQLite database from our existing France corner evidence, then query the overall counts, opponent-level summaries, extra-time events and a five-row preview. SQL reproduces the existing research rather than changing its definitions or adding new observations.

**Result:** 45 corner deliveries, 19 associated with a shot, 21 phase shots and two goals. The pooled corner-shot rate is **19/45 = 42.22%**. The extra-time query returns three Brazil deliveries.

Opponent query results are Korea Republic 6/13, Norway 3/9, Nigeria 4/9, Brazil 2/7 and USA 4/7 corners associated with a shot. These are the same small-sample descriptive counts as the original study, not new tactical findings.

## Database, table, row and column

SQLite stores structured records in a local database file. Our `corners` table is a collection of rows with named columns. **One row is one corner delivery**, including deliveries with no shot. A corner with two phase shots is still one row with `phase_shots = 2` and `has_phase_shot = 1`.

This row definition is the table's grain. It preserves the correct rate denominator. A table whose rows were individual shots would answer a different question and omit corners without shots unless explicitly joined back to the delivery table.

The table contains source match/corner IDs, opponent/date, period/time, phase shot count, goal count and a 0/1 indicator for any phase shot. A combined primary key prevents duplicate source deliveries. Constraints reject negative counts, impossible goal totals and inconsistent shot indicators.

## Read the first query

```sql
SELECT COUNT(*)
FROM corners;
```

`FROM corners` identifies the source table. `COUNT(*)` counts all its rows. `SELECT` returns the requested result. The query returns **45**. SQL is the language used to ask the database for records and summaries; Python creates the database and runs our saved query files.

Filtering adds `WHERE`. For example:

```sql
SELECT COUNT(*)
FROM corners
WHERE period IN (3, 4);
```

This returns **3**, selecting extra-time rows. `GROUP BY opponent` gathers rows per opponent so count and sum can be calculated for each group. The full query in `sql/54_by_opponent.sql` keeps all deliveries in each denominator, including those without a shot.

`SUM(has_phase_shot)` counts positive corners because its values are 0 or 1. It differs from `SUM(phase_shots)`: one phase can contain multiple shots. Multiply by `100.0` to preserve decimal division, and use `NULLIF` when a zero denominator should remain undefined. Tables have no guaranteed display order, so the preview and event queries use explicit `ORDER BY`; `LIMIT 5` restricts the preview.

## Run locally in Spyder

Open and run `54_first_football_sql.py` using the project interpreter. It uses Python's `sqlite3` module and needs no new Python package in the existing environment. It creates the disposable generated file `data/local/54_corners.sqlite3`, saves readable query evidence in `data/54_first_sql_evidence.json` and prints results.

The database is rebuilt on each run; keep durable query edits in the committed `.sql` files. Generated database bytes are ignored by Git because the source JSON, schema, query files and outputs already reproduce it. Database binary hashes are not used for cross-platform research evidence.

The SQL files are:

- `sql/54_schema.sql`: table structure and integrity rules.
- `sql/54_overall.sql`: all-delivery totals and rate.
- `sql/54_by_opponent.sql`: grouped opponent results.
- `sql/54_extra_time.sql`: filtered event records.
- `sql/54_sample.sql`: ordered preview.

Values are inserted with parameter binding, so player/opponent names containing apostrophes remain text rather than SQL code. The `SELECT` queries read records; they do not modify the database.

## Employment connection and honest status

This adds a practical SQL work sample to the Python portfolio: a defined table, auditable loading, filtering and grouped aggregates. It is a first guided exercise, not proof of SQL proficiency or mastery of joins, window functions or production databases. Independent reproduction and a small query modification remain separate learning milestones.

**Completed worked assignment:** create the database and reproduce all original counts through SQL. Independent practice when ready: modify the filtering query to count first-half deliveries, explain its denominator, then ask the teacher to check the result. Do not label this independent task as completed before it is done.

Sources: [SQLite SELECT documentation](https://www.sqlite.org/lang_select.html) and [Python 3.11 sqlite3 tutorial](https://docs.python.org/3.11/library/sqlite3.html). Data: StatsBomb Open Data. No new football model or fresh validation.
