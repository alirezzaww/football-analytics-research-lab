# Look behind the shortlisted player averages

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Case study: spreadsheet scouting](https://soccermatics.readthedocs.io/en/latest/lesson3/SpreadsheetScout.html); SQL: [SQLite SUM and AVG](https://www.sqlite.org/lang_aggfunc.html). Custom guided tool extension.

The original four-profile shortlist now has a match drill-down. The database contains 145 player–match activity rows for all 35 profiles. Every player's match counts and registered milliseconds reconcile exactly to the existing profile. Source event IDs remain in the saved evidence.

## Lucy Bronze — England Women's

Pooled rate: 34 forward completions / 691.184200 minutes ×90 = **4.4272/90** across 7 included fixtures. Observed match rates span 1.89–6.67/90. An equally weighted mean of match rates is 4.3922/90; that answers a different weighting question.

- 2019-06-09 vs Scotland W: 7 fixed-rule forward completions in 96.64 registered minutes = **6.52/90**; 66 eligible completions; 22 pressures. Match 22936.
- 2019-06-14 vs Argentina Women's: 5 fixed-rule forward completions in 96.37 registered minutes = **4.67/90**; 37 eligible completions; 12 pressures. Match 22962.
- 2019-06-19 vs Japan Women's: 2 fixed-rule forward completions in 95.05 registered minutes = **1.89/90**; 51 eligible completions; 27 pressures. Match 68337.
- 2019-06-23 vs Cameroon W: 8 fixed-rule forward completions in 107.90 registered minutes = **6.67/90**; 55 eligible completions; 9 pressures. Match 68362.
- 2019-06-27 vs Norway Women's: 5 fixed-rule forward completions in 96.72 registered minutes = **4.65/90**; 44 eligible completions; 6 pressures. Match 69199.
- 2019-07-02 vs United States Women's: 3 fixed-rule forward completions in 98.08 registered minutes = **2.75/90**; 50 eligible completions; 18 pressures. Match 69258.
- 2019-07-06 vs Sweden Women's: 4 fixed-rule forward completions in 100.42 registered minutes = **3.58/90**; 47 eligible completions; 8 pressures. Match 69301.
## Desiree van Lunteren — Netherlands Women's

Pooled rate: 34 forward completions / 723.975650 minutes ×90 = **4.2267/90** across 7 included fixtures. Observed match rates span 0.91–8.11/90. An equally weighted mean of match rates is 4.2788/90; that answers a different weighting question.

- 2019-06-11 vs New Zealand Women's: 6 fixed-rule forward completions in 96.70 registered minutes = **5.58/90**; 56 eligible completions; 10 pressures. Match 22942.
- 2019-06-15 vs Cameroon W: 6 fixed-rule forward completions in 95.57 registered minutes = **5.65/90**; 21 eligible completions; 10 pressures. Match 22964.
- 2019-06-20 vs Canada Women's: 2 fixed-rule forward completions in 97.16 registered minutes = **1.85/90**; 17 eligible completions; 24 pressures. Match 68344.
- 2019-06-25 vs Japan Women's: 5 fixed-rule forward completions in 98.56 registered minutes = **4.57/90**; 53 eligible completions; 15 pressures. Match 69188.
- 2019-06-29 vs Italy Women's: 9 fixed-rule forward completions in 99.88 registered minutes = **8.11/90**; 52 eligible completions; 3 pressures. Match 69205.
- 2019-07-03 vs Sweden Women's: 5 fixed-rule forward completions in 137.21 registered minutes = **3.28/90**; 50 eligible completions; 16 pressures. Match 69284.
- 2019-07-07 vs United States Women's: 1 fixed-rule forward completions in 98.88 registered minutes = **0.91/90**; 20 eligible completions; 8 pressures. Match 69321.
## Ashley Elizabeth Marie Lawrence — Canada Women's

Pooled rate: 10 forward completions / 291.588017 minutes ×90 = **3.0865/90** across 3 included fixtures. Observed match rates span 0.93–4.77/90. An equally weighted mean of match rates is 3.0979/90; that answers a different weighting question.

- 2019-06-10 vs Cameroon W: 5 fixed-rule forward completions in 94.32 registered minutes = **4.77/90**; 48 eligible completions; 9 pressures. Match 22939.
- 2019-06-20 vs Netherlands Women's: 1 fixed-rule forward completions in 97.16 registered minutes = **0.93/90**; 30 eligible completions; 22 pressures. Match 68344.
- 2019-06-24 vs Sweden Women's: 4 fixed-rule forward completions in 100.11 registered minutes = **3.60/90**; 28 eligible completions; 26 pressures. Match 69163.
## Risa Shimizu — Japan Women's

Pooled rate: 13 forward completions / 382.961017 minutes ×90 = **3.0551/90** across 4 included fixtures. Observed match rates span 0.95–5.63/90. An equally weighted mean of match rates is 3.0638/90; that answers a different weighting question.

- 2019-06-10 vs Argentina Women's: 6 fixed-rule forward completions in 95.98 registered minutes = **5.63/90**; 63 eligible completions; 13 pressures. Match 22940.
- 2019-06-14 vs Scotland W: 4 fixed-rule forward completions in 93.37 registered minutes = **3.86/90**; 39 eligible completions; 7 pressures. Match 22961.
- 2019-06-19 vs England Women's: 1 fixed-rule forward completions in 95.05 registered minutes = **0.95/90**; 38 eligible completions; 5 pressures. Match 68337.
- 2019-06-25 vs Netherlands Women's: 2 fixed-rule forward completions in 98.56 registered minutes = **1.83/90**; 28 eligible completions; 11 pressures. Match 69188.

## Read the averages correctly

A pooled per90 rate describes all selected playing time together. It does not imply the same activity in every game. Calculate total actions / total minutes ×90; averaging match rates gives each match equal weight even if the player played different durations. A short registered interval can produce a high rate from few actions. The min–max range above describes only the included matches; it is not a confidence interval or a forecast.

The database has one row per player–fixture, joined to one parent player profile with the full compound key. Pass, forward-pass and pressure counts are assembled at this grain before joining; joining raw event tables could multiply counts. The existing qualifying_fixtures table supplies the foreign-key membership check. Both source fixture membership and clock-window coverage are verified.

This view identifies matches worth inspecting, not why a rate differed. Opponent strength, score state, possession, instructions, role changes and opportunities are not adjusted here. A high or low match value alone is not a performance judgement. No new shortlist, model, player-quality grade or footage observation is introduced.

## Run locally

Run `python 84_scouting_match_drilldown.py` in Spyder to rebuild the local database and report. Or use `python 84_scouting_match_drilldown.py --team-id 865 --player-id 10178` from the project directory to print Bronze's included matches. The original database stays unchanged; this extension is saved at `data/local/84_scouting_drilldown.sqlite3` and ignored by Git.

[Match rows, event IDs and source hashes](../data/84_scouting_match_drilldown_evidence.json) · [Schema](../sql/84_match_activity_schema.sql) · [Player query](../sql/84_player_matches.sql) · [Totals query](../sql/84_player_totals.sql) · [Lesson](../lessons/0066-scouting-match-drilldown.html).
Assisted implementation; independent query construction and interpretation remain to demonstrate.
