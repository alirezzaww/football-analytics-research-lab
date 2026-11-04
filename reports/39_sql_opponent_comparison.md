# SQL opponent comparison: France corner phases

The joined-table query reproduces the existing five-match corner results, preserving one row per delivery before calculating opponent rates. No new data or model was added.

- USA: 4 of 7 corners led to a shot (57.1%); 4 phase shots.
- Korea Republic: 6 of 13 (46.2%); 7 phase shots.
- Nigeria: 4 of 9 (44.4%); 4 phase shots.
- Norway: 3 of 9 (33.3%); 4 phase shots.
- Brazil: 2 of 7 (28.6%); 2 phase shots.

Overall: 19 of 45 corners (42.2%), producing 21 phase shots. The numerator counts corners with any shot, not the number of shots. The overall rate pools counts rather than averaging match percentages.

## Reproduce

Run `python 56_sql_opponent_comparison.py` locally or in Spyder. It rebuilds in-memory relational tables using lesson 55 and executes [the SQL query](../sql/56_opponent_corner_rates.sql). [Saved evidence](../data/56_sql_opponent_evidence.json) includes source and query hashes. No new dependency is required.

1. Group phase shots by the full match/corner key.
2. LEFT JOIN those summaries to all corner deliveries, retaining zero-shot corners.
3. GROUP BY opponent and calculate counts and percentages.
4. ORDER BY the rate descending for display.

## Interpretation and limits

USA has the highest observed rate in this sample, while Korea has the most phase shots. Each opponent appears in one match; differences do not isolate defensive ability, tactics or match context. The phase definition remains lesson 38's same-possession, at-most-15-second rule with its restart/period boundaries, including extra time. These associations are not direct assists or proof that a corner caused a shot.

This is an assisted worked SQL exercise, not evidence of independent proficiency. [Short lesson](../lessons/0038-sql-opponent-comparison.html). Primary SQL source: [SQLite SELECT](https://www.sqlite.org/lang_select.html).
