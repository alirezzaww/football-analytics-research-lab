# Passing activity with matched score-state time

Data: **2019 FIFA Women's World Cup**, StatsBomb competition 72 / season 30.
Reading: [Soccermatics Lesson 3 — Normalisation](https://soccermatics.readthedocs.io/en/latest/lesson3/ScoutingPlayers.html#normalisation); [SQLite CASE and expressions](https://www.sqlite.org/lang_expr.html). This is our custom score-context extension.

Earlier score-state work counted actions while leading/drawing/trailing. Here each count is paired with registered time in that same state. All 435 player–match–state rows reconcile to the original 145 player–match rows, and the 105 player-state aggregates reconcile to all 35 profiles. Reconstructed final scores match metadata in all 50 included fixtures.

## Lucy Bronze — England Women's

- **Leading**: 19 fixed-rule forward completions in 386.71 registered minutes → 4.42/90; 206 eligible completions; 57 pressures.
- **Drawing**: 8 fixed-rule forward completions in 137.59 registered minutes → 5.23/90; 66 eligible completions; 25 pressures.
- **Trailing**: 7 fixed-rule forward completions in 166.88 registered minutes → 3.78/90; 78 eligible completions; 20 pressures.
## Desiree van Lunteren — Netherlands Women's

- **Leading**: 7 fixed-rule forward completions in 163.68 registered minutes → 3.85/90; 38 eligible completions; 26 pressures.
- **Drawing**: 26 fixed-rule forward completions in 526.17 registered minutes → 4.45/90; 221 eligible completions; 57 pressures.
- **Trailing**: 1 fixed-rule forward completions in 34.13 registered minutes → 2.64/90; 10 eligible completions; 3 pressures.
## Ashley Elizabeth Marie Lawrence — Canada Women's

- **Leading**: 2 fixed-rule forward completions in 49.80 registered minutes → 3.61/90; 17 eligible completions; 4 pressures.
- **Drawing**: 6 fixed-rule forward completions in 172.40 registered minutes → 3.13/90; 71 eligible completions; 43 pressures.
- **Trailing**: 2 fixed-rule forward completions in 69.39 registered minutes → 2.59/90; 18 eligible completions; 10 pressures.
## Risa Shimizu — Japan Women's

- **Leading**: 2 fixed-rule forward completions in 71.11 registered minutes → 2.53/90; 24 eligible completions; 6 pressures.
- **Drawing**: 9 fixed-rule forward completions in 198.24 registered minutes → 4.09/90; 104 eligible completions; 24 pressures.
- **Trailing**: 2 fixed-rule forward completions in 113.61 registered minutes → 1.58/90; 40 eligible completions; 6 pressures.

## Exact conventions

Use the existing raw event-index goal accounting: Shot/Goal or Own Goal Against, ignoring its Own Goal For counterpart and shootouts. Count each selected action in the state immediately before it by event index. Split registered elapsed milliseconds at logged goal timestamps, with the score updated at that timestamp. Period lengths and no-halftime-gap convention come from lesson 64; added and extra time remain. Logged goal-event start times approximate the instant the score changed; event index resolves ties for actions while clock overlap determines duration.

A goal may therefore change the state partway through one player's registered interval. All three states remain present, including zero-exposure states. Rates use SUM(actions)*5,400,000/NULLIF(SUM(state milliseconds),0). No exposure gives an undefined rate, not zero performance. A boundary action can be retained even with zero measured duration for that state; its rate remains undefined. Counts and time are pooled before division, not averaged across match/state rates.

## Interpretation

These rates describe activity in different observed circumstances. They do not establish that leading or trailing caused a change: opponents, match phase, tactics, possession and role remain intertwined. Short state exposure can give a large rate from few actions; always inspect counts and minutes. A state appearing in only a few fixtures is not equivalent to a broad repeated comparison. No signing recommendation or new shortlist is generated. No footage has been reviewed.

## Reproduce

Run `python 85_scouting_score_context.py` in Spyder. The new local database is `data/local/85_scouting_score_context.sqlite3`; earlier databases remain unchanged. [Protocol](../data/85_score_state_protocol.json) · [State rows, action IDs, goal audits and source hashes](../data/85_scouting_score_context_evidence.json) · [SQL rates](../sql/85_score_state_rates.sql) · [Lesson](../lessons/0067-scouting-score-context.html).
Source: StatsBomb Open Data. Assisted implementation; independent reasoning and reproduction remain learning milestones.
