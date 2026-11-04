# Lesson 55: connect corner and shot records without changing the denominator

## Completed worked assignment

Separate the existing France study into two related tables:

- `corners`: **45 rows**, one per delivery, including zero-shot corners.
- `phase_shots`: **21 rows**, one per shot associated with a corner under the fixed phase rule.

Each shot references a corner using **both match ID and corner ID**. A foreign key rejects shots pointing to a nonexistent delivery. The shot's match/shot primary key prevents duplicate assignment. This is the same audited phase association, not newly inferred direct assisting-pass linkage.

## Read a join

```sql
SELECT c.opponent, s.shot_id
FROM corners AS c
LEFT JOIN phase_shots AS s
    ON c.match_id = s.match_id
   AND c.corner_id = s.corner_id;
```

`c` and `s` are short aliases. `ON` specifies how records match. `LEFT JOIN` keeps every corner, even when it has no matching phase-shot row. Those corners have NULL in the shot columns.

For a small illustration:

```text
Corner A → Shot 1
Corner A → Shot 2
Corner B → NULL
```

There are **three joined rows but only two corner deliveries**. The repeated Corner A is expected in a one-to-many relationship. It does not mean the original delivery table has duplicate events.

## What happened in our actual database

The direct left join produces **47 rows**: 21 matched shot rows plus 26 corners without an associated shot. Two of the 19 shot-associated corners each contain two shots, accounting for the two extra rows beyond the original 45 deliveries.

- `COUNT(*)` on this join counts **47 joined rows**.
- `COUNT(s.shot_id)` counts **21 non-NULL linked shot rows**.
- Neither of those is the correct delivery denominator of **45**.

An inner join would return the 21 matched shot rows and omit the 26 zero-shot corners. It therefore changes the population and still repeats corners with multiple shots. This is why joining tables requires checking the grain and retaining the appropriate exposure.

## Preserve the denominator

The worked solution in `sql/55_corner_summary.sql` first groups shots to one row per match/corner. Then it left-joins that summary to the 45-delivery table. The result is exactly:

**45 deliveries, 19 corners with a shot, 21 phase shots, two goals, and 19/45 = 42.22%.**

The opening `WITH shots_per_corner AS (...)` names the intermediate result. You do not need to memorize that syntax yet: understand the purpose, which is to restore one result row per corner before calculating a delivery-level rate.

A foreign key protects relationship existence, not a football interpretation. NULL here means no matching record under our defined phase association; it does not prove the corner created no threat outside that rule. No new observations, model or causal claim are introduced.

## Run and inspect

Run `python 55_football_sql_joins.py` in Spyder. It rebuilds the disposable local file `data/local/55_corner_relationships.sqlite3` from saved source evidence, leaving lesson 54's database separate. SQL files are `sql/55_schema.sql`, `55_join_preview.sql`, `55_join_diagnostic.sql` and `55_corner_summary.sql`. Query outputs and both input tables are committed as `data/55_sql_join_evidence.json`; the binary database is ignored by Git.

The script explicitly enables SQLite foreign-key enforcement before inserts, binds data values as parameters, and checks database/foreign-key integrity. Each query uses the documented complete key; the preview specifies its result order.

Tests check multi-shot row expansion, zero-shot corner retention, same corner identifiers in different matches, orphan rejection and duplicate shots. Evidence checks reconstruct both input tables, counts, query results and optional local database records.

**Completed assignment:** build and join two tables, demonstrate the misleading 47-row count, and reproduce the correct delivery summary. Independent practice remains separate: explain why joining cannot create extra source corners, then ask your teacher to review your wording.

Sources: [SQLite SELECT and join processing](https://www.sqlite.org/lang_select.html) and [SQLite foreign-key support](https://www.sqlite.org/foreignkeys.html). Data: StatsBomb Open Data. Guided implementation; independent SQL proficiency is not claimed.
