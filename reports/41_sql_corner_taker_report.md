# France corner-taker SQL report

Question: who delivered France's corners, and how often were those deliveries associated with a shot under our existing phase rule?

- Amel Majri: 10/24 corners with a shot (41.7%); 12 phase shots, 1 shot goals.
- Gaëtane Thiney: 8/18 corners with a shot (44.4%); 8 phase shots, 1 shot goals.
- Onema Grace Geyoro: 0/2 corners with a shot (0.0%); 0 phase shots, 0 shot goals.
- Elise Bussaglia: 1/1 corners with a shot (100.0%); 1 phase shots, 0 shot goals.

All four groups sum to 45 deliveries, 19 corners with a shot, 21 phase shots and two shot goals. Goals are phase outcomes, not credited assists. Display order is delivery volume, not a ranking of ability.

## The SQL workflow

The existing corner table identifies deliveries; the new corner_takers table adds one recorded passer name per full match/corner key. The loader rejects missing, duplicate or extra metadata before joining, so the inner metadata join cannot silently drop a corner. Shots are grouped per corner before the left join to preserve the delivery denominator.

GROUP BY passer creates a summary for each name in this sample. HAVING COUNT(*) >= :min_deliveries filters those completed groups. At the illustrative threshold of 10, the displayed names are Amel Majri, Gaëtane Thiney. All-player results remain saved and visible above. Parameters are bound as values rather than interpolated SQL text.

WHERE filters input rows before grouping; HAVING filters resulting groups. Filtering to shot-positive corners before counting would remove unsuccessful deliveries from the denominator and answer a different question.

## Football interpretation

Bussaglia's 1/1 is 100%, but one attempt does not establish a better taker than Majri's 10/24. Ten is only an example display rule: it is not a statistically justified sample-size threshold, and 24 attempts do not establish stable player ability either. No significance test was run. This descriptive report is not a recommendation to change the taker.

The earlier taker/side analysis found different delivery contexts. This report does not adjust for side, technique, opponent, runners or defenders. Only the existing five France fixtures are included, with the unchanged 15-second same-possession phase rule and its restart/period boundaries. Name labels are used because the saved source provides them; a larger multi-team player database should use stable player IDs rather than assume names are unique.

## Reproduce

Run `python 58_sql_corner_taker_report.py` locally or in Spyder. Read [the SQL](../sql/58_corner_taker_report.sql), [saved evidence](../data/58_sql_corner_taker_evidence.json) and [short lesson](../lessons/0040-sql-corner-taker-report.html). The assignment was completed with assistance; independent query construction remains to demonstrate.

Primary source: [SQLite SELECT, GROUP BY and HAVING](https://www.sqlite.org/lang_select.html). Football source: StatsBomb Open Data through the existing lesson 38 and 39 ledgers.
