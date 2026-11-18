# A reusable SQL scouting database

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting](https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html); SQL reference: [SQLite window functions](https://www.sqlite.org/windowfunctions.html).
This is our custom SQL extension, not a SQL exercise copied from Soccermatics.

## What was built

The existing passing, fixed forward-pass and recorded pressure counts now share a local SQLite database with 35 player profiles and 145 qualifying player–fixture memberships. The second count is not 145 distinct matches or players. Stable compound IDs prevent duplicate profiles; the fixture table links to its parent using foreign keys. The generated database is ignored by Git; source SQL, rebuilding code and evidence are public.

- left_only: 17 profiles.
- right_only: 14 profiles.
- mixed: 4 profiles.

## First queries

- **Lucy Bronze**: right_only; 45.57 completed passes/90; passing-activity rank 1 in 14 eligible profiles in that side group.
- **Amel Majri**: left_only; 30.70 completed passes/90; passing-activity rank 7 in 17 eligible profiles in that side group.

Ranks sort passing activity, not player quality. All original values and selected fixtures remain unchanged. No composite score or validated recruitment criterion is introduced.

## New SQL concept: rank within a group

```sql
DENSE_RANK() OVER (
    PARTITION BY side_group
    ORDER BY completed_per90 DESC
)
```

PARTITION BY gives each side group its own comparison. DENSE_RANK gives tied values equal ranks: 10,10,8 → ranks1,1,2. Unlike GROUP BY, it keeps each player's row. The activity rate is calculated from full precision counts/time; display rounding does not create ties.

The query's eligible CTE applies role/minimum-start filters before ranking, so ranks and peer counts refer to that returned eligible pool. Mixed-side players are kept separate rather than silently assigned to left/right. Original cohort membership was at least three qualifying starts; raising the query minimum narrows this existing pool, while omitted players cannot be recovered by lowering a SQL filter. A rank of1 means highest measured passing activity in the eligible side pool, not best fullback.

## Run locally

In Spyder, run `81_scouting_database.py`. Or from the project directory:

```sh
python 81_scouting_database.py --side right_only --min-starts 3
python 81_scouting_database.py --side left_only --min-starts 4
```

The generated database is `data/local/81_scouting.sqlite3`. The script always rebuilds canonical three-start evidence; the CLI then prints your exploratory filtered query without rewriting the original cohort results. Values are bound as SQL parameters. No app installation or browser notebook is required; sqlite3 is included with Python.

## Evidence and limits

fullbacks: one competition/season/team/player profile. qualifying_fixtures: one included player-fixture membership, not a unique tournament fixture or an additional player.

Rates are calculated in SQL from unchanged counts and registered milliseconds: count*5,400,000/duration_ms. Percentage denominators use NULLIF for missing exposure. No mean of match rates.

Per90 normalizes registered time, not possession, difficulty or time strictly in the fullback position. The forward rule remains end_x−start_x≥20 coordinate units; Pressure counts describe provider-recorded starts, not successful defending. A single-metric order is an inspection starting point; compare football roles and further evidence before making judgements.

[Saved rows, source/SQL hashes and query results](../data/81_scouting_database_evidence.json) · [Schema](../sql/81_scouting_schema.sql) · [Parameterized query](../sql/81_role_activity.sql) · [Lesson](../lessons/0063-scouting-database.html).
Assisted implementation; independent SQL construction and explanation remain to demonstrate.
