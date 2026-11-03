# Lesson 30: when did the chances arrive?

The previous match brief described totals. This extension adds timing to the same France–Korea Republic fixture, using exactly the same 26 shots and frozen distance-only model probabilities. There is no refit, new data collection or fresh validation.

France accumulated **1.445 model npxG from 16 first-half shots**, then **0.198 from five second-half shots**. Korea Republic accumulated **0.009 from one first-half shot**, then **0.149 from four second-half shots**. The final totals reconcile to lesson 29: 1.643 and 0.157.

France's estimated chance generation was concentrated in the first half. Korea Republic generated more model npxG in the second half than in the first. This is a descriptive timing comparison, not evidence for a tactical or score-state cause. The halves have different stoppage-time exposure, and these are raw totals rather than per-minute rates.

## Read the staircase

Each included shot adds its probability to the team's previous total, whether scored or missed. A 0.20 shot increases the line by 0.20. Stars mark goals but do not add an extra point to the curve. Flat stretches mean no included shots, not necessarily no possession, pressure or threatening attacks. The chart does not represent live win probability.

First- and second-half clocks occupy separate panels. First-half added time remains in period 1; nominal second-half minutes are shifted by 45. The second panel carries the first-half cumulative total forward. Plot extents are 45 nominal minutes or the last observed shot, whichever is later; these are not independently reconstructed whistle times. Recorded whole seconds are used, with stable source-ledger ordering for shots tied within a second. This simple two-period implementation rejects extra time rather than silently combining it.

## Reproduce

Run `python 30_cumulative_xg_timeline.py` in Spyder. It reads the committed `data/29_match_xg_evidence.json`, saves its SHA256 lineage and shot-by-shot running totals in `data/30_cumulative_xg_evidence.json`, and writes `figures/33_cumulative_xg_timeline.png`. It needs no raw cache or network. Unit tests independently reconcile every step, half and final team total; they cover first-half added time, second-half carry-forward and empty team halves.

The model remains an educational distance-only fit trained on 114 shots, and these are not StatsBomb's supplied xG values. Penalties, shootouts and own-goal events remain outside the included shot set. No goals-minus-xG claim about finishing talent follows from one match.

Data: [StatsBomb Open Data](https://github.com/statsbomb/open-data). Foundation: [Soccermatics xG model fitting](https://soccermatics.readthedocs.io/en/latest/gallery/lesson2/plot_xGModelFit.html). A separate R package offers a [cumulative xG timeline example](https://jogall.github.io/2019-01-16-adjusted-xG/); it is not the Python course or a dependency of this implementation. This lesson is an original project extension.

Prepared with assistance. Independent task: explain France's first/second-half contrast in two sentences and identify a match-video question to investigate. A useful question is what changed in shot locations or attacking patterns after halftime; the chart alone cannot answer it. Independent interpretation remains pending.
