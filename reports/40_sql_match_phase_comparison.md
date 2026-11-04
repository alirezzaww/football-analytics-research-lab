# France corner rates by match phase

SQL CASE labels each delivery using its recorded period, then GROUP BY pools corners with the same label across the existing five France fixtures.

- First half: 10/24 corners with a shot (41.7%); 12 phase shots.
- Second half: 8/18 corners with a shot (44.4%); 8 phase shots.
- Extra time: 1/3 corners with a shot (33.3%); 1 phase shots.

The second-half observed rate is slightly higher, but the first half produced more phase shots. These are different measures. The counts sum to 45 deliveries, 19 corners with a shot and 21 shots, matching the original study.

## Definition and interpretation

- Period 1 means first half, including its added time. A period-1 corner at minute 46 is not a second-half corner.
- Period 2 means second half, including added time. Periods 3 and 4 are pooled as extra time.
- The source schema permits only periods 1–4, so the CASE ELSE branch contains only extra time. The query would need revisiting for a different schema including shootouts.
- Extra time contains only three corners from the Brazil match, not five matches of comparable exposure. It is kept separate.
- Rates describe the fraction of corners associated with a shot, not corners or shots per minute. Phase lengths and game context differ.
- A small descriptive difference does not establish improvement after half-time, a coach effect, or a statistically reliable difference. No significance test was run.
- Groups with no deliveries are absent from the query result; absence is not a measured 0% rate.

The existing 15-second same-possession phase rule and restart/period boundaries remain unchanged. All corners, including zero-shot corners, remain in their group's denominator. Shots are summarized by full match/corner key before the join.

## Reproduce and learn

Run `python 57_sql_match_phase_comparison.py` in the local environment or Spyder. Read [the query](../sql/57_corner_half_rates.sql), [saved evidence](../data/57_sql_match_phase_evidence.json) and [short lesson](../lessons/0039-sql-match-phase-comparison.html).

This is an assisted assignment. Independently explaining and modifying the query remains to demonstrate. Primary source: [SQLite CASE expressions](https://www.sqlite.org/lang_expr.html#the_case_expression).
