# Phase 3 / Lesson 44: first position-based expected-threat model

## Completed worked assignment

We start a new modelling block following [Soccermatics position-based xT](https://soccermatics.readthedocs.io/en/latest/gallery/lesson4/plot_ExpectedThreat.html) and the [official mplsoccer xT tutorial](https://mplsoccer.readthedocs.io/en/latest/gallery/tutorials/plot_xt.html). Our original implementation fits a deliberately coarse **6×4 grid** using both teams in the five existing France fixtures.

The selected training data contain **6,770 actions: 3,447 passes, 3,204 carries and 119 shots, including 11 shot goals**. This is a training visualization and calculation exercise, not independently validated scoring probabilities or a player-ranking study.

Position-based xT assigns a value to possessing the ball in each zone under a simplified action model. For an observed completed move, **added xT = value at end − value at start**. Unlike a shot-only model, this can assign values to earlier ball progression even when the next action is not a shot.

## How the model is fitted

1. Divide normalized 120×80 coordinates into six columns and four rows; each cell spans 20×20 coordinate units. Row zero is nearest y=0, and attacks point toward x=120. Exact outer boundaries remain in the last cell; out-of-pitch starts are excluded rather than clipped.
2. Count considered actions starting in each cell. Eligible actions are possession-team Pass, Carry and non-penalty Shot events in periods 1–4. Restart passes are excluded. Both teams contribute to the fit.
3. Immediate reward is shot goals divided by all considered actions in a cell. This equals shot frequency multiplied by empirical goal frequency given a shot.
4. For each pair of cells, successful movement count divided by all considered starting actions gives a transition weight. Failed passes remain in the denominator and contribute no continuing transition. Carries with in-pitch endpoints continue; completed passes require no recorded outcome and an in-pitch endpoint. Missing/outside endpoints have no continuing transition.
5. Repeatedly update each zone value as immediate reward plus weighted destination values. Stop when the largest update is at most 1e-12, with a 10,000-iteration cap. Here convergence takes **139 iterations**, with fixed-point residual about **8.12e-13**.

The direct successful-transition/action form is algebraically equivalent to the tutorial's move probability multiplied by successful-transition probability conditional on a move. All 24 cells have observed actions here; in other samples an unobserved cell would retain zero by convention and must be flagged by its zero action count rather than described as a known safe zone.

## Three actual pass examples

The earliest completed France pass in event order of each sign is selected for demonstration, not as a performance test:

- Delphine Cascarino: start value **0.007757**, end **0.009224**, added xT **+0.001467**.
- Wendie Renard: start/end **0.013004**, added xT **0**. Within-cell movement is invisible to this coarse model; zero does not mean no football contribution.
- Eugénie Le Sommer: start **0.013004**, end **0.009224**, added xT **−0.003780**. This means a lower-valued destination under this grid, not proof of a bad decision.

Exact coordinates, match/event IDs, cell memberships and full-precision values are saved. Do not describe the positive example as necessarily a forward pass: this location-only grid is not simply a distance ranking, and its learned lateral differences are noisy in this small sample.

## What to understand and what remains untested

**xG estimates a shot's scoring chance. Position-based xT values a ball location under a model of what actions may follow.** Added xT is a signed change between locations. It is not shot xG, a pass-completion probability or causal player credit.

The simplifying assumption is that continuation value depends only on the grid location, not the sequence, pressure, defenders, taker or game state. Shots terminate this simple transition model, so their miss/rebound continuation is not explicitly modelled. Failed moves have zero continuation, without modelling the opponent's counterattack. Filtering out restarts and non-possession-team actions further defines the fitted action population; these values must not be read as empirically calibrated full-possession probabilities.

The examples score completed passes only. A full player assessment would need an explicit failed-action valuation and opportunity/context handling, rather than ranking players solely on these selected positive or completed actions. No out-of-sample test or calibration was performed; all values and examples reuse the fitting sample. This new model does not alter the frozen xG model or the passing case study's provider xG.

## Reproduce and audit

Run `python 44_first_expected_threat.py`. It uses the five hash-verified raw files already recorded in the France study and downloads only missing caches. Outputs: `data/44_first_xt_evidence.json` and `figures/46_first_expected_threat.png`. Saved records include every eligible action, counts, transition matrix, zone values, convergence diagnostics, exclusions and worked examples.

Tests cover pitch boundaries, retention of failed movements in denominators and known fixed-point solutions. Evidence checks reconstruct counts/transitions, verify probability mass and the Bellman residual, reproduce pass scores and, when raw caches exist, reconstruct action selection and coordinates from the original events. Numerical convergence is a computation check, not proof of real-world model accuracy.

Implementation and assignment completed with assistance. Sources: Soccermatics and mplsoccer tutorials above; data: StatsBomb Open Data. This is an educational project extension; independent user mastery is not claimed.
